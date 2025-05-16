from dataclasses import dataclass, field
from typing import Any, Final, LiteralString


_DEFAULT_EXCHANGE_RATES: Final[dict[LiteralString, float]] = {"USD": 0.0122, "EUR": 0.0100, "RUR": 1.0}


@dataclass
class Options:
    """Options collected from a config file and command line flags.

    Options
    ----------
    query_params : dict[str, Any]
        Params for GET request to API
    num_workers : int
        Number of parallel workers for threading
    exchange_rates : dict[str, float]
        Exchange rates for different currencies to RUR
    save_results_to_csv : bool
        Save results to CSV file
    """

    query_params: dict[str, Any] | None = None
    num_workers: int = 1
    exchange_rates: dict[str, float] = field(default_factory=lambda: _DEFAULT_EXCHANGE_RATES)
    save_results_to_csv: bool = False

    def __repr__(self) -> str:
        opts: Final = ", ".join([f"{k}: {v}" for k, v in self.__dict__.items()])
        return f"{self.__class__.__name__}({opts})"
