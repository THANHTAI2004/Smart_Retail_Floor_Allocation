# Vai trò: Các endpoint cho danh mục dữ liệu, cấu hình, campaign và báo cáo nghiên cứu.
# Yêu cầu chạy tạo tiến trình giám sát; HTTP không trực tiếp giải bài toán số.
"""HTTP adapters for local synthetic research campaigns."""

from fastapi import APIRouter
from fastapi.responses import FileResponse

from smart_retail.application.experiments import service
from smart_retail.contracts.experiments import CampaignSpec

router = APIRouter(prefix="/api/research", tags=["Research"])


@router.get("/datasets")
# Hàm datasets: xử lý bước datasets trong phạm vi module hiện tại.
def datasets():
    return service.catalog()


@router.get("/configurations")
# Hàm configurations: xử lý bước configurations trong phạm vi module hiện tại.
def configurations():
    return service.configurations()


@router.get("/campaigns")
# Hàm campaigns: xử lý bước campaigns trong phạm vi module hiện tại.
def campaigns():
    return service.listing()


@router.post("/campaigns", status_code=202)
# Hàm start: xử lý bước start trong phạm vi module hiện tại.
def start(spec: CampaignSpec):
    return service.launch(spec)


@router.get("/campaigns/{identifier}")
# Hàm detail: xử lý bước detail trong phạm vi module hiện tại.
def detail(identifier: str):
    return service.detail(identifier)


@router.get("/campaigns/{identifier}/jobs/{job_key}/joint")
# Hàm joint_result: xử lý bước joint result trong phạm vi module hiện tại.
def joint_result(identifier: str, job_key: str):
    return service.joint_result(identifier, job_key)


@router.post("/campaigns/{identifier}/cancel", status_code=202)
# Hàm cancel: gửi hoặc ghi nhận yêu cầu hủy theo trạng thái hiện tại.
def cancel(identifier: str):
    return service.cancel(identifier)


@router.post("/campaigns/{identifier}/resume", status_code=202)
# Hàm resume: xử lý bước resume trong phạm vi module hiện tại.
def resume(identifier: str):
    value = service.detail(identifier)
    return service.launch(
        CampaignSpec.model_validate(value["configuration"]), identifier=identifier, resume=True
    )


@router.post("/campaigns/{identifier}/replay", status_code=202)
# Hàm replay: kiểm tra lại quyết định từ đầu vào gốc.
def replay(identifier: str):
    value = service.detail(identifier)
    return service.launch(CampaignSpec.model_validate(value["configuration"]))


@router.get("/campaigns/{identifier}/report/{relative:path}")
# Hàm download: xử lý bước download trong phạm vi module hiện tại.
def download(identifier: str, relative: str):
    path = service.report_file(identifier, relative)
    return FileResponse(path, filename=path.name)
