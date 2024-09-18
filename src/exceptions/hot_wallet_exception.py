class HotWalletException(Exception):
     """Critical exception, execution cannot continue. The browser will stop."""
     
     def __init__(self, *args):
        super().__init__(args)