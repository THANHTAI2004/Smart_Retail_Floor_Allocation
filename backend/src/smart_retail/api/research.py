"""HTTP adapters for local synthetic research campaigns."""

from fastapi import APIRouter
from fastapi.responses import FileResponse

from smart_retail.application.experiments import service
from smart_retail.contracts.experiments import CampaignSpec

router = APIRouter(prefix="/api/research", tags=["Research"])


@router.get("/datasets")
def datasets():
    return service.catalog()


@router.get("/configurations")
def configurations():
    return service.configurations()


@router.get("/campaigns")
def campaigns():
    return service.listing()


@router.post("/campaigns", status_code=202)
def start(spec: CampaignSpec):
    return service.launch(spec)


@router.get("/campaigns/{identifier}")
def detail(identifier: str):
    return service.detail(identifier)


@router.get("/campaigns/{identifier}/jobs/{job_key}/joint")
def joint_result(identifier: str, job_key: str):
    return service.joint_result(identifier, job_key)


@router.post("/campaigns/{identifier}/cancel", status_code=202)
def cancel(identifier: str):
    return service.cancel(identifier)


@router.post("/campaigns/{identifier}/resume", status_code=202)
def resume(identifier: str):
    value = service.detail(identifier)
    return service.launch(
        CampaignSpec.model_validate(value["configuration"]), identifier=identifier, resume=True
    )


@router.post("/campaigns/{identifier}/replay", status_code=202)
def replay(identifier: str):
    value = service.detail(identifier)
    return service.launch(CampaignSpec.model_validate(value["configuration"]))


@router.get("/campaigns/{identifier}/report/{relative:path}")
def download(identifier: str, relative: str):
    path = service.report_file(identifier, relative)
    return FileResponse(path, filename=path.name)
