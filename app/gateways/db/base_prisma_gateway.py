from typing import Any

from app.gateways.db.prisma_client import (
    payload_to_dict,
    prisma_client,
    prisma_result,
    run_prisma,
)
from app.gateways.result import GatewayResult


class BasePrismaGateway:
    def __init__(self):
        self.prisma = prisma_client()

    def _model(self, name: str):
        return getattr(self.prisma, name)

    def create(self, model_name: str, payload: Any) -> GatewayResult[Any]:
        model = self._model(model_name)
        return prisma_result(model.create(data=payload_to_dict(payload)))

    def find_many(
        self, model_name: str, where: dict[str, Any] | None = None, **kwargs
    ) -> GatewayResult[list[Any]]:
        model = self._model(model_name)
        return prisma_result(model.find_many(where=where or {}, **kwargs))

    def update_many_and_fetch(
        self, model_name: str, where: dict[str, Any], payload: Any
    ) -> GatewayResult[list[Any]]:
        model = self._model(model_name)
        try:
            run_prisma(model.update_many(where=where, data=payload_to_dict(payload)))
            updated = run_prisma(model.find_many(where=where))
            return {"success": True, "message": ["Success"], "data": updated}
        except Exception as exc:
            return {"success": False, "message": [str(exc)], "data": None}

    def delete_many_and_return_before(
        self, model_name: str, where: dict[str, Any]
    ) -> GatewayResult[list[Any]]:
        model = self._model(model_name)
        try:
            records = run_prisma(model.find_many(where=where))
            run_prisma(model.delete_many(where=where))
            return {"success": True, "message": ["Success"], "data": records}
        except Exception as exc:
            return {"success": False, "message": [str(exc)], "data": None}
