import asyncio
from abc import abstractmethod

from typing import Dict, Union
import pandas as pd

from aiohttp import web
from aiohttp.web_fileresponse import FileResponse

from scipy.interpolate import interp1d

router = web.RouteTableDef()


class Server:
    def __init__(self) -> None:
        pass

    @router.get("/")
    async def serve_index(self, request: web.Request) -> web.FileResponse:
        return web.FileResponse("./index.html")




class GenericTable:

    def __init__(self, path_2_raw_file: str) -> None:
        self._file = path_2_raw_file

        # internal properties
        self._df: pd.DataFrame

    async def initialize(self, ):
        """
        This doesn't really need to be asyncronous. pandas read_csv is blocking. not anymore succkers
        """
        self._df = await asyncio.to_thread(pd.read_csv, self._file)

        # do the initialization
        self._my_init()

    @abstractmethod
    async def _my_init(self, ) -> None:
        pass


    def calculate(self, *args, **kwargs) -> None:
        self._calc(*args, **kwargs)

    @staticmethod
    def _calc(self, *args, **kwargs) -> float:
        pass


class SatWaterPressure(GenericTable):

    NAME = "Saturated Water Pressure"

    def __init__(self, path_2_raw_file: str) -> None:
        super().__init__(path_2_raw_file)

        self._interp_funcs: Dict[str, interp1d] = {}

    def _my_init(self) -> None:
        """
        should you cache all forms of interpolation for speed?, 
        I think this needs to be a nested forloop to get all combos
        """
        for col in ['enthalpy', 'internal_energy', ...]:
            for inner_col in [...]:
                self._interp_funcs["-".join(col, inner_col)] = interp1d(
                    x=self._df[inner_col],
                    y=self._df[col]
                )

    def _calc(self, var_1: dict, var_2: dict) -> float:
        """
        Really this should return more than 1 variable.
        """ 
        self._interp_funcs["-".join(var_1['name'], var_2['name'])](
            x=var_1['val'],
            y=var_2['val']
        )

    

        
class UserSession:

    """
    I think it makes sense to save that last query from the user, 
    as they will likely want similar information or information related to the last query

    Could also do this with a websocket and start the calculation as soon as the user enters data

    This has to be handled differently than the rest of the code though, as it must not get overriden by concurrent web visitors
    """



class Api:
    def __init__(self, steam_table_path: str) -> None:

        self._tables: Dict[
            str, GenericTable 
        ] = {}  # eventually this should be a mapping of subclasses


    async def setup(self, steam_table_mapping: Dict[str, GenericTable]) -> None:
        self._tables = {obj.NAME: obj(file_path) for file_path, obj in steam_table_mapping}
        
        await asyncio.gather(
            *(
                obj(file_path).initialize() for obj, file_path in steam_table_mapping.items()
             )
        )


    @router.post('/api')
    async def calculate(self, request: web.Request) -> web.Response:
        """
        We obvi have to come up with a standard request format
        """
        _r = request.json()
        response = await self._tables[_r["table"]](_r['data'])
        return response



async def init_app() -> web.Application:

    # create the server
    server = Server()

    # create the api
    api = Api("there should be a file path here")
    await api.setup(
        {
            "./file located here": SatWaterPressure,
        }
    )

    app = web.Application()
    app.add_routes(router)
    return app


if __name__ == "__main__":

    web.run_app(init_app())
