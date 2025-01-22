from __future__ import annotations

from bson import ObjectId

from constants.versions import Version


def testFromTuple(name: str, typeName: str, version: Version, wins: list[ObjectId]) -> ObjectId:
    return {"_id": ObjectId(), "name": name, "objectType": typeName, "version": version,
            "winDescriptionIdList": wins}


def patchDB(
    wins: list[tuple[str, ...]], tests: list[tuple[str, str, Version, list[int]]]
) -> tuple[list[ObjectId], list[ObjectId]]:
    winDescriptions = [{"_id": ObjectId(), "outputPath": list(code)} for code in wins]
    tests = [testFromTuple(*data, [winDescriptions[i]["_id"]
                                           for i in wins]) for *data, wins in tests]

    return winDescriptions, tests
