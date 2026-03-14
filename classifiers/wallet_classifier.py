"""
wallet_classifier.py
====================
自己ウォレット判定モジュール。

config/wallets.json にユーザー所有アドレスを列挙することで、
同一ユーザー間のトランザクションを SELF_TRANSFER として識別します。

使い方:
    from classifiers.wallet_classifier import WalletClassifier
    wc = WalletClassifier()
    if wc.is_self_transfer(from_addr, to_addr):
        tx_type = "SELF_TRANSFER"
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# config/wallets.json のデフォルトパス
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "wallets.json"


class WalletClassifier:
    """
    自己ウォレット判定クラス。

    config/wallets.json からユーザーアドレスを読み込み、
    from / to の両方がユーザー所有なら SELF_TRANSFER と判定します。
    """

    def __init__(self, config_path: Path | None = None):
        self._addresses: set[str] = set()
        path = config_path or DEFAULT_CONFIG_PATH
        self._load(path)

    def _load(self, path: Path) -> None:
        """wallets.json からアドレスリストを読み込む。"""
        if not path.exists():
            logger.debug("wallets.json が見つかりません: %s (自己ウォレット判定を無効化)", path)
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            addresses = data.get("addresses", [])
            self._addresses = {a.strip().lower() for a in addresses if a.strip()}
            if self._addresses:
                logger.info("自己ウォレット: %d 件読み込み済み", len(self._addresses))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("wallets.json の読み込みエラー: %s", exc)

    @property
    def addresses(self) -> set[str]:
        """ユーザー所有アドレスのセット (lowercase)。"""
        return self._addresses

    def is_own_address(self, addr: str) -> bool:
        """指定アドレスがユーザー所有かどうか判定。"""
        return addr.lower() in self._addresses

    def is_self_transfer(self, from_addr: str, to_addr: str) -> bool:
        """
        from / to の両方がユーザー所有アドレスなら True。
        ウォレットリストが空の場合は常に False を返す。
        """
        if not self._addresses:
            return False
        return self.is_own_address(from_addr) and self.is_own_address(to_addr)


# モジュールレベルのシングルトン (キャッシュ用)
_instance: WalletClassifier | None = None


def get_wallet_classifier(config_path: Path | None = None) -> WalletClassifier:
    """モジュールレベルのシングルトンを返す。"""
    global _instance
    if _instance is None:
        _instance = WalletClassifier(config_path)
    return _instance
