from pathlib import Path

examples_path_root = Path(__file__).parent

XML_PATH_MAP = {
    "1687": {
        "1": examples_path_root / "nirvar/example1.xml",
        "2": examples_path_root / "nirvar/example2.xml",
        "3": examples_path_root / "nirvar/example3.xml",
        "4": examples_path_root / "nirvar/example4.xml",
        "5": examples_path_root / "nirvar/example5.xml",
    }
}


def get_xml_file_path(action_type: str, example_number_str: str) -> Path | None:
    """
    Returns XML Path based on action_type and caller_code.
        action_type - predefined string with integer, based on https://ws.registrucentras.lt/broker/info.php
        example_number_str - string with integer that determines which example file to use, if
                             multiple example files exist for same action_type
    """
    return XML_PATH_MAP.get(action_type, {}).get(example_number_str)
