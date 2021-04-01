from datetime import datetime

from serenity.analytics.api import SnapshotId, Mode


def test_snapshot_id():
    ts_str = '20200926160000'
    ts = datetime.strptime(ts_str, '%Y%m%d%H%M%S')
    snapshot_id = SnapshotId(Mode.BACKTEST, 'BBands1', ts)
    snapshot_id_txt = str(snapshot_id)
    assert snapshot_id_txt == f'BACKTEST/BBands1/{ts_str}'
