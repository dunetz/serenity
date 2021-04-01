Internals & Architecture
========================

Serenity is fundamentally a two-tier architecture system at this time, mediated by an object-relational
database layer written in a mix of custom code and `sqlalchemy <http://www.sqlalchemy.org/>`_. This design
is not very popular today with the advance of cloud-based microservices, but it's practical for the
target audience of individual or small groups of quants developing, backtesting and deploying algos, and it
does not preclude adding a third tier in future for wider-scale deployments.

Package map
-----------

:py:mod:`serenity.algo` contains a complete reactive algo engine based on the `Tau <https://pypi.org/project/pytau/>`_
library, with both live and backtest versions. This is the older of the two backtesting API's, and
the plan is to merge it with :py:mod:`serenity.strategy` in the 0.10.x release. (See :doc:`roadmap`.) If
you are interested in cryptocurrency trading this is the place to start.

:py:mod:`serenity.booker` is incomplete, but will eventually contain trade booking to the database.

:py:mod:`serenity.db` is a bit of a mess. It contains a bespoke object-relational layer which
will be replaced by sqlalchemy in the 0.10.x release, plus a helper script
for backfilling reference data from different exchanges. This needs a lot of work.

:py:mod:`serenity.equity` contains a complete batch pipeline and object model for the
`Sharadar <http://sharadar.com>`_ equity research database on `Quandl <http://quandl.com>`_. If you
are interested in equity trading this is a good place to start.

:py:mod:`serenity.exchange` contains utilities for integrating with different exchanges. Right now
only `Phemex <http://phemex.com/>`_ has code here.

:py:mod:`serenity.marketdata` is some of the oldest code in the system, and contains a number of
websocket clients for exchange feedhandlers: Binance, Coinbase Pro and Phemex. Again, Phemex is
the best supported at this time. There is also an upload script which runs daily and uploads
the tick-by-tick marketdata recorded by the feedhandlers to both a Parquet-based flat file store
and to Azure blob storage. The latter is an essential component for tick-by-tick backtesting and
so it's worth a look if you are looking at :py:mod:`serenity.algo` as well.

:py:mod:`serenity.model` is the object model that goes with :py:mod:`serenity.db` and will
be merged with it in 0.10.x when we switch to sqlalchemy.

:py:mod:`serenity.pnl` and :py:mod`serenity.position` are incomplete, but will eventually contain
the position keeper and marking / P&L / risk services. This is not terribly well thought out and
:py:mod:`serenity.strategy` takes a different approach which probably needs to be reconciled.

:py:mod:`serenity.signal` has some extensions to Tau's Signal API for things like computing OHLC
and Bollinger Bands. There is extensive work in the open source world on Pandas-based technical
analysis (TA) libraries, but these several classes show how to reformulate some of those algorithms
in a reactive programming paradigm. For anyone interested in :doc:`contributing` there is a lot
of work that could be done here to create a unit-tested library of TA algorithms.

:py:mod:`serenity.model` is the object model that goes with :py:mod:`serenity.db` and will
be merged with it in 0.10.x when we switch to sqlalchemy.

:py:mod:`serenity.strategy` integrates Tau with a higher-level API for close-on-close
investment strategies, with an emphasis on equity trading strategies. Currently this package
has a dependency on Sharadar, but it should be possible to integrate free resources like
Yahoo Finance's API.

:py:mod:`serenity.tax` has a script for generating a TurboTax export file for taxes plus
several other scripts from backfilling trade data from different exchanges. This is very
rough and needs to be totally redone.

:py:mod:`serenity.trading` is an abstraction sitting on top of exchange connectivity, e.g. REST
API's for cryptocurrency exchanges. It is currently implemented for Phemex and for a simple
exchange simulator. For anyone interested in :doc:`contributing` a Coinbase Pro implementation
and Gemini implementation of this API would be nice small projects.

Python version
--------------

We use `Azure DevOps <http://dev.azure.com/>`_ for continuous integration services, and
the build pipeline currently runs all tests against both Python 3.7 and 3.8, so code should
be compatible with both versions.
