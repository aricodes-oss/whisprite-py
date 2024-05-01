from typing import List, Tuple, Callable, Dict, Any

CommandMapping = List[Tuple[str, Callable[..., any], Dict[str, Any] | None]]
