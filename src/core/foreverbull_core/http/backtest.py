from typing import List

import requests
from foreverbull_core.http import RequestError
from foreverbull_core.models import backtest, service


class Backtest:
    def __init__(self, host: str, session: requests.Session = None) -> None:
        """Initializes Backtest service client api

        Args:
            host (str): Host address to the Foreverbull backend server. IP:PORT Format
            session (requests.Session, optional): Use pre defined session instead of creating new. Defaults to None.
        """
        self.host = host
        if session is None:
            session = requests.Session()
        self.session = session

    def list(self) -> List[backtest.EngineConfig]:
        """Lists stored backtest from Server

        Raises:
            RequestError: In case response code is not OK

        Returns:
            List[backtest.EngineConfig]: List of configuration for Backtests stored on Server
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/backtests")
        if not rsp.ok:
            raise RequestError(
                f"""get call /backtests gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return [backtest.EngineConfig(**b) for b in rsp.json()]

    def create(self, backtest: backtest.EngineConfig) -> backtest.EngineConfig:
        """Creates and stores a new Backtest on the Server

        Args:
            backtest (backtest.EngineConfig): Configuration for the backtest to be stored

        Raises:
            RequestError: In case response code is not OK

        Returns:
            backtest.EngineConfig: Stored, newly created, backtest.
        """
        rsp = self.session.post(f"http://{self.host}/api/v1/backtests", json=backtest.dict())
        if not rsp.ok:
            raise RequestError(
                f"""post call /backtests gave bad return code: {rsp.status_code}"
            Text: {rsp.text}"""
            )
        return backtest.update_fields(rsp.json())

    def get(self, backtest_id: str) -> backtest.EngineConfig:
        """Retrieve a stored backtest based on backtest ID

        Args:
            backtest_id (str): Identifier of the backtest

        Raises:
            RequestError: In case response code is not OK

        Returns:
            backtest.EngineConfig: Full configuration of the stored Backtest
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/backtests/{backtest_id}")
        if not rsp.ok:
            raise RequestError(
                f"""get call /backtests/{backtest_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return backtest.EngineConfig(**rsp.json())

    def delete(self, backtest_id: str) -> None:
        """Delete a stored backtest, based on backtest_id

        Args:
            backtest_id (str): Identifier or the backtest

        Raises:
            RequestError: In case response code is not OK

        Returns:
            None:
        """
        rsp = self.session.delete(f"http://{self.host}/api/v1/backtests/{backtest_id}")
        if not rsp.ok:
            raise RequestError(
                f"""delete call /backtests/{backtest_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return None

    def list_sessions(self, backtest_id: str) -> List[backtest.Session]:
        """List sessions of a Backtest stored in Database

        Args:
            backtest_id (str): Identified for the backtest

        Raises:
            RequestError: In case response code is not OK

        Returns:
            List[backtest.Session]: List of Sessions for that backtest
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions")
        if not rsp.ok:
            raise RequestError(
                f"""get call /backtests/{backtest_id}/sessions gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return [backtest.Session(**s) for s in rsp.json()]

    def create_session(self, backtest_id: str, session: backtest.Session) -> backtest.Session:
        """Create and store a new Session, connected to a stored Backtest

        Args:
            backtest_id (str): Identified of the Backtest where the session is base on
            session (backtest.Session): Required information about the Session

        Raises:
            RequestError: In case response code is not OK

        Returns:
            backtest.Session: Created and stored Session
        """
        rsp = self.session.post(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions", json=session.dict())
        if not rsp.ok:
            raise RequestError(
                f"""post call /backtests/{backtest_id}/sessions gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return session.update_fields(rsp.json())

    def get_session(self, backtest_id: str, session_id: str) -> backtest.Session:
        """Get a stored backtest session from Server

        Args:
            backtest_id (str): Identifier of the backtest
            session_id (str): Identifier of the session

        Raises:
            RequestError: In case response code is not OK

        Returns:
            backtest.Session: Stored backtest session
        """
        rsp = self.session.get(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}")
        if not rsp.ok:
            raise RequestError(
                f"""get call /backtests/{backtest_id}/sessions/{session_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return backtest.Session(**rsp.json())

    def delete_session(self, backtest_id: str, session_id: str) -> None:
        """Deletes a stored backtest session from Server

        Args:
            backtest_id (str): Identifier of the backtest
            session_id (str): Identifier of the session

        Raises:
            RequestError: In case response code is not OK

        Returns:
            None:
        """
        rsp = self.session.delete(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}")
        if not rsp.ok:
            raise RequestError(
                f"""delete call /backtests/{backtest_id}/sessions/{session_id} gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return None

    def setup_session(self, backtest_id: str, session_id: str) -> None:
        """Manually setup the backtest session execution

        Args:
            backtest_id (str): Identifier of the backtest
            session_id (str): Identifier of the session

        Raises:
            RequestError: In case response code is not OK

        Returns:
            None:
        """
        rsp = self.session.post(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}/setup")
        if not rsp.ok:
            code = rsp.status_code  # to mitigate line too long
            raise RequestError(
                f"""post call /backtests/{backtest_id}/sessions/{session_id}/setup gave bad return code: {code}
            Text: {rsp.text}"""
            )
        return None

    def configure_session(self, backtest_id: str, session_id: str, raw_conn: service.RawConnection = None) -> None:
        """Manually configure the backtest session execution

        Args:
            backtest_id (str): Identifier of the backtest
            session_id (str): Identifier of the session

        Raises:
            RequestError: In case response code is not OK

        Returns:
            None:
        """
        rsp = self.session.post(
            f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}/configure", json=raw_conn.dict()
        )
        if not rsp.ok:
            code = rsp.status_code  # to mitigate line too long
            raise RequestError(
                f"""post call /backtests/{backtest_id}/sessions/{session_id}/configure gave bad return code: {code}
            Text: {rsp.text}"""
            )
        return None

    def run_session(self, backtest_id: str, session_id: str) -> None:
        """Manually run the backtest session execution

        Args:
            backtest_id (str): Identifier of the backtest
            session_id (str): Identifier of the session

        Raises:
            RequestError: In case response code is not OK

        Returns:
            None:
        """
        rsp = self.session.post(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}/run")
        if not rsp.ok:
            raise RequestError(
                f"""post call /backtests/{backtest_id}/sessions/{session_id}/run gave bad return code: {rsp.status_code}
            Text: {rsp.text}"""
            )
        return None

    def stop_session(self, backtest_id: str, session_id: str) -> None:
        """Manually stop the backtest session execution

        Args:
            backtest_id (str): Identifier of the backtest
            session_id (str): Identifier of the session

        Raises:
            RequestError: In case response code is not OK

        Returns:
            None:
        """
        rsp = self.session.post(f"http://{self.host}/api/v1/backtests/{backtest_id}/sessions/{session_id}/stop")
        if not rsp.ok:
            raise RequestError(
                f"""post call /backtests/{backtest_id}/sessions/{session_id}/stop gave bad return code: {rsp.status_code} Text: {rsp.text}"""  # noqa: E501
            )
        return None
