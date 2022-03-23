from typing import List

from fastapi import APIRouter
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from deciphon_api.csched import ffi, lib
from deciphon_api.errors import EINVAL, ErrorResponse, InternalError
from deciphon_api.models.seq import Seq
from deciphon_api.rc import RC

router = APIRouter()


@router.get(
    "/seqs/{seq_id}",
    summary="get sequence",
    response_model=List[Seq],
    status_code=HTTP_200_OK,
    responses={
        HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    name="seqs:get-sequence",
)
def get_sequence(seq_id: int):
    cseq = ffi.new("struct sched_seq *")
    cseq[0].id = seq_id

    rc = RC(lib.sched_seq_get(cseq))
    assert rc != RC.END

    if rc == RC.NOTFOUND:
        raise EINVAL(HTTP_404_NOT_FOUND, "job not found")

    if rc != RC.OK:
        raise InternalError(HTTP_500_INTERNAL_SERVER_ERROR, rc)

    return Seq.from_cdata(cseq)
