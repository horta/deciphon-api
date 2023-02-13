from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from deciphon_api.api.utils import AUTH
from deciphon_api.errors import FileNotInStorageError
from deciphon_api.journal import get_journal
from deciphon_api.models import (
    DB,
    Job,
    JobType,
    Scan,
    ScanCreate,
    ScanRead,
    Seq,
    SeqRead,
    Snap,
    SnapCreate,
    SnapRead,
)
from deciphon_api.sched import Sched, select
from deciphon_api.snap_validate import snap_validate
from deciphon_api.storage import storage_has

__all__ = ["router"]

router = APIRouter()

OK = HTTP_200_OK
NO_CONTENT = HTTP_204_NO_CONTENT
CREATED = HTTP_201_CREATED


@router.get("/scans", response_model=List[ScanRead], status_code=OK)
async def read_scans():
    with Sched() as sched:
        return [ScanRead.from_orm(x) for x in sched.exec(select(Scan)).all()]


@router.post("/scans/", response_model=ScanRead, status_code=CREATED)
async def create_scan(scan: ScanCreate):
    with Sched() as sched:
        sched.get(DB, scan.db_id)

        x = Scan.from_orm(scan)
        x.job = Job(type=JobType.scan)
        x.seqs = [Seq.from_orm(i) for i in scan.seqs]
        sched.add(x)
        sched.commit()
        sched.refresh(x)
        y = ScanRead.from_orm(x)
        await get_journal().publish_scan(y.id)
        return y


@router.get("/scans/{scan_id}", response_model=ScanRead, status_code=OK)
async def read_scan(scan_id: int):
    with Sched() as sched:
        return ScanRead.from_orm(sched.get(Scan, scan_id))


@router.delete("/scans/{scan_id}", status_code=NO_CONTENT, dependencies=AUTH)
async def delete_scan(scan_id: int):
    with Sched() as sched:
        sched.delete(sched.get(Scan, scan_id))
        sched.commit()


@router.get("/scans/{scan_id}/seqs", response_model=List[SeqRead], status_code=OK)
async def read_seqs(scan_id: int):
    with Sched() as sched:
        scan = sched.get(Scan, scan_id)
        return [SeqRead.from_orm(i) for i in scan.seqs]


@router.put("/scans/{scan_id}/snap.dcs", response_model=SnapRead, status_code=CREATED)
async def create_snap(scan_id: int, snap: SnapCreate):
    if not storage_has(snap.sha256):
        raise FileNotInStorageError(snap.sha256)

    with Sched() as sched:
        scan = sched.get(Scan, scan_id)
        snap_validate(scan_id, scan.seqs, snap)
        x = Snap.from_orm(snap, update={"scan_id": scan_id})
        x.scan_id = scan_id
        sched.add(x)
        sched.commit()
        sched.refresh(x)
        return SnapRead.from_orm(x)


@router.get("/scans/{scan_id}/snap.dcs", response_model=SnapRead, status_code=OK)
async def read_snap(scan_id: int):
    with Sched() as sched:
        scan = sched.get(Scan, scan_id)
        return SnapRead.from_orm(scan.snap)
