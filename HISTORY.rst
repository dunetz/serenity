.. :changelog:

Release History
---------------

0.9.0 (TBD January 2021)
++++++++++++++++++++++++

- Secured AzureBlobTickstore by switching to Azure AD credentials for read-only
- Integrated documentation with http://readthedocs.org
- Improved API docstrings

0.8.0 (2021-01-01)
++++++++++++++++++

- Extensive support for Sharadar equity fundamentals research database
- Brand new InvestmentStrategy API and backtester for stock trading
- Upgraded to latest Tau reactive library (0.14)

0.7.0 (2020-10-31)
++++++++++++++++++

- Support for distributed backtests with Dask

0.6.0 (2020-10-03)
++++++++++++++++++

- Major upgrade to Tau reactive framework to address threading issues
- refactored modules to use api.py rather than __init__.py
- Fixed bug in extra outputs handling in live & backtest modes
- Further strategy improvements

0.5.1 (2020-09-28)
++++++++++++++++++

- Added DataCaptureService and integrated with live & backtest modes
- Fixed reconnection logic for all Phemex websocket-based interfaces

0.5.0 (2020-09-26)
++++++++++++++++++

- Added support for stop orders in live & backtest modes
- Added PositionService, ExchangePositionService and OrderManagerService
- Refactored AutoFillSimulator and Phemex trading connector to use OMS
- Upgraded pytau to 0.8.0 to ensure stable sorts in backtest mode
- Refined bbands1.py example strategy

0.4.0 (2020-09-20)
++++++++++++++++++

- Added support for tick-by-tick backtester
- Added Bollinger Bands trading strategy example
- Fixed bug in Azure cloud storage layer

0.3.4 (2020-09-11)
++++++++++++++++++

- Add missing dependencies in setup.py

0.3.3 (2020-09-11)
++++++++++++++++++

- Various small fixes for JupyterLab Kubernetes

0.3.2 (2020-09-11)
++++++++++++++++++

- Started capturing top of order book for Phemex
- Integrated Azure blob storage with behemoth_upload.py
- Upgraded libraries for Serenity & JupyterLab

0.3.1 (2020-08-16)
++++++++++++++++++

- Fixed broken test

0.3.0 (2020-08-16)
++++++++++++++++++

- Added support for streaming Bollinger Band computation
- Added Azure blob storage option for tickstores
- Upgraded to Tau 0.5.0

0.2.0 (2020-05-03)
++++++++++++++++++

- Added basic strategy API with dummy example
- Implemented runnable MVP version of algo engine
- Supported extending mmap journal files on-the-fly
- Improved Azure DevOps integration, including Python 3.7/3.8 cross-build
- Upgraded to Tau 0.4.3

0.1.3 (2020-04-30)
++++++++++++++++++

- Upgraded to Tau 0.4.0
- Cleaned up requirements.txt; removed tornado & APScheduler

0.1.2 (2020-04-26)
++++++++++++++++++

- Upgraded to Tau 0.3.1 to pick up critical bug fix

0.1.1 (2020-04-26)
++++++++++++++++++

- Additional fixes for Tickstore bi-temporal index logic

0.1.0 (2020-04-25)
++++++++++++++++++

- Refactored PhemexFeedHandler
- Added CoinbaseProFeedHandler
- Added BinanceFeedHandler
- Critical fixes for Tickstore bi-temporal index logic
- Upgraded to Tau 0.3.0

0.0.3 (2020-04-19)
+++++++++++++++++++

- Added new generic FeedHandler API
- Implemented PhemexFeedHandler
- Converted Phemex tick upload job to Kubernetes CronJob
- Moved Tickstore and Journal from serenity.mdrecorder to serenity.tickstore
- Critical fix for buy/sell code mapping in Phemex feed
- Upgraded to pandas 1.0.3

0.0.2 (2020-04-13)
+++++++++++++++++++

- Fixed dependencies in setup.py

0.0.1 (2020-04-13)
+++++++++++++++++++

- Initial implementation
