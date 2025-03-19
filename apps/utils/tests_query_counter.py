from django.db import DEFAULT_DB_ALIAS, connections
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient


class QueryLimitExceededError(ValueError):
    pass


class APIClientWithQueryCounter(APIClient):
    """
    APIClient, which on all HTTP request calls asserts Django DB query count to be
    not greater than some configured limit.
    """

    def __init__(self, count: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = count

    def get(self, *args, **kwargs):
        with self._assert_num_queries("GET", *args, **kwargs):
            return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        with self._assert_num_queries("POST", *args, **kwargs):
            return super().post(*args, **kwargs)

    def put(self, *args, **kwargs):
        with self._assert_num_queries("PUT", *args, **kwargs):
            return super().put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        with self._assert_num_queries("PATCH", *args, **kwargs):
            return super().patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with self._assert_num_queries("DELETE", *args, **kwargs):
            return super().delete(*args, **kwargs)

    def _assert_num_queries(self, http_method: str, *args, **kwargs):
        url = args[0] if args else kwargs.get("path")
        request_key = f"{http_method} {url}"
        query_limit = kwargs.get("query_limit")
        max_query_limit = query_limit if isinstance(query_limit, int) else self.count
        connection = connections[DEFAULT_DB_ALIAS]
        return AssertMaxNumQueriesContext(connection, max_query_limit, request_key)


class AssertMaxNumQueriesContext(CaptureQueriesContext):
    def __init__(
        self,
        connection,
        max_query_limit: int,
        request_key: str,
    ):
        self.max_query_limit = max_query_limit
        self.request_key = request_key
        super().__init__(connection)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        if exc_type is not None:
            return

        filtered_queries = [
            query["sql"] for query in self.captured_queries if self._include_query_in_results(query["sql"])
        ]
        executed = len(filtered_queries)
        ok = executed <= self.max_query_limit

        if not ok:
            error_message_lines = [
                f"Too many queries. Executed: {executed}, limit: {self.max_query_limit}.",
                f"Request: {self.request_key}",
                "",
                "TIP: if there is good reason for that, you can raise the limit per request",
                f"by making sure key '{self.request_key}' (or any substring of it) exists",
                "in field query_limits in your TestCase.",
                "",
                "Query summary:",
            ]
            error_message_lines.extend(
                f"{index + 1}. {self._get_query_summary(query)}" for index, query in enumerate(filtered_queries)
            )
            error_message_lines.extend(
                [
                    "",
                    "Queries:",
                ]
            )
            error_message_lines.extend(f"{index + 1}. {query}" for index, query in enumerate(filtered_queries))

            error_msg = "\n\n".join(error_message_lines)
            raise QueryLimitExceededError(error_msg)

    def _include_query_in_results(self, query: str) -> bool:
        return "SAVEPOINT" not in query  # For now exclude queries, which are for transaction handling

    def _get_query_summary(self, query: str) -> str:
        parts = query.split(" ")
        start = parts[0]

        if start == "SELECT" or start == "DELETE":
            index = self._last_index(parts, "FROM")
            table_name = parts[index + 1] if index and index + 1 < len(parts) else ""
            return f"{start} FROM {table_name}"
        if start == "INSERT":
            index = parts.index("INTO")
            table_name = parts[index + 1] if index and index + 1 < len(parts) else ""
            return f"{start} INTO {table_name}"
        if start == "UPDATE":
            table_name = parts[1] if len(parts) > 1 else ""
            return f"{start} {table_name}"
        return "?"

    def _last_index(self, ls, value):
        return len(ls) - ls[::-1].index(value) - 1
