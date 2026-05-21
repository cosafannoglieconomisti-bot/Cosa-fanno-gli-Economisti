import json
import logging
import os
import re
import urllib.parse
import httpx
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .models import Notebook, Source, Asset

logger = logging.getLogger("pp_notebooklm.client")

class NotebookLMClient:
    BASE_URL = "https://notebooklm.google.com"
    BATCHEXECUTE_URL = f"{BASE_URL}/_/LabsTailwindUi/data/batchexecute"

    RPC_LIST_NOTEBOOKS = "wXbhsf"
    RPC_GET_NOTEBOOK = "rLM1Ne"
    RPC_ADD_SOURCE = "izAoDd"
    RPC_CREATE_STUDIO = "R7cb6c"
    RPC_POLL_STUDIO = "gArtLc"

    def __init__(self):
        self.auth_data = self._load_auth()
        self.cookies = self.auth_data.get("cookies", {})
        self.csrf_token = self.auth_data.get("csrf_token", "")
        self.session_id = self.auth_data.get("session_id", "")
        self._client: Optional[httpx.Client] = None

    def _load_auth(self) -> Dict:
        auth_path = Path.home() / ".notebooklm-mcp" / "auth.json"
        if not auth_path.exists():
            raise FileNotFoundError("Auth file not found. Run notebooklm-mcp-auth first.")
        with open(auth_path, "r") as f:
            return json.load(f)

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            cookie_str = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
            self._client = httpx.Client(
                headers={
                    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                    "Cookie": cookie_str,
                    "X-Same-Domain": "1",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                },
                timeout=60.0,
            )
        return self._client

    def _call_rpc(self, rpc_id: str, params: Any) -> Any:
        client = self._get_client()
        
        # Build body
        params_json = json.dumps(params, separators=(',', ':'))
        f_req = [[[rpc_id, params_json, None, "generic"]]]
        f_req_json = json.dumps(f_req, separators=(',', ':'))
        body = f"f.req={urllib.parse.quote(f_req_json, safe='')}"
        if self.csrf_token:
            body += f"&at={urllib.parse.quote(self.csrf_token, safe='')}"
        body += "&"

        # Build URL
        url_params = {"rpcids": rpc_id, "rt": "c"}
        if self.session_id:
            url_params["f.sid"] = self.session_id
        url = f"{self.BATCHEXECUTE_URL}?{urllib.parse.urlencode(url_params)}"

        response = client.post(url, content=body)
        response.raise_for_status()
        
        return self._parse_response(response.text, rpc_id)

    def _parse_response(self, text: str, rpc_id: str) -> Any:
        if text.startswith(")]}'"):
            text = text[4:]
        
        # Simple extraction for batchexecute
        # format is complex, but we can look for the specific chunk
        lines = text.strip().split("\n")
        for i, line in enumerate(lines):
            try:
                data = json.loads(line)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, list) and len(item) >= 3:
                            if item[0] == "wrb.fr" and item[1] == rpc_id:
                                result_str = item[2]
                                if isinstance(result_str, str):
                                    return json.loads(result_str)
                                return result_str
            except:
                continue
        return None

    def list_notebooks(self) -> List[Notebook]:
        # [null, 1, null, [2]]
        result = self._call_rpc(self.RPC_LIST_NOTEBOOKS, [None, 1, None, [2]])
        notebooks = []
        if not result:
            return notebooks

        # Find any nested list where items look like [ title, sources, id, ... ]
        def find_list_of_notebooks(data):
            if not isinstance(data, list):
                return None
            
            # Check if this list itself is a list of notebooks
            valid_items = 0
            for item in data:
                if isinstance(item, list) and len(item) >= 3:
                    potential_id = item[2]
                    while isinstance(potential_id, list) and len(potential_id) > 0:
                        potential_id = potential_id[0]
                    if isinstance(item[0], str) and isinstance(potential_id, str) and len(potential_id) == 36:
                        valid_items += 1
            
            if valid_items > 0:
                return data
            
            # Otherwise recurse
            for item in data:
                res = find_list_of_notebooks(item)
                if res:
                    return res
            return None

        nb_list = find_list_of_notebooks(result)
        if not nb_list:
            return notebooks
        
        for item in nb_list:
            try:
                title = item[0]
                raw_id = item[2]
                while isinstance(raw_id, list) and len(raw_id) > 0:
                    raw_id = raw_id[0]
                
                nb_id = str(raw_id)
                sources_data = item[1] if len(item) > 1 else []
                source_count = len(sources_data) if isinstance(sources_data, list) else 0
                
                nb = Notebook(
                    id=nb_id,
                    title=title,
                    source_count=source_count,
                    is_owned=True
                )
                notebooks.append(nb)
            except (IndexError, TypeError):
                continue
        return notebooks

    def get_notebook_details(self, notebook_id: str) -> Dict:
        # [notebook_id, null, null, [2]]
        return self._call_rpc(self.RPC_GET_NOTEBOOK, [notebook_id, None, None, [2]])

    def poll_studio(self, notebook_id: str) -> List[Asset]:
        # [[2], notebook_id, 'NOT artifact.status = "ARTIFACT_STATUS_SUGGESTED"']
        params = [[2], notebook_id, 'NOT artifact.status = "ARTIFACT_STATUS_SUGGESTED"']
        result = self._call_rpc(self.RPC_POLL_STUDIO, params)
        
        assets = []
        if not result or not isinstance(result, list):
            return assets
            
        # Structure is [ [artifact1, artifact2, ...] ] or [artifact1, artifact2, ...]
        artifact_list = result[0] if isinstance(result[0], list) and len(result[0]) > 0 and isinstance(result[0][0], list) else result
        
        type_map = {
            1: "audio",
            2: "report",
            3: "video",
            4: "flashcards",
            7: "infographic",
            8: "slide_deck",
            9: "data_table"
        }
        
        for art in artifact_list:
            print(f"DEBUG: Raw artifact: {art}")
            if not isinstance(art, list) or len(art) < 5:
                continue
            
            art_id = art[0]
            title = art[1]
            type_code = art[2]
            status_code = art[4] # 1: in_progress, 3: completed
            
            asset_type = type_map.get(type_code, "unknown")
            if status_code == 3:
                status = "completed"
            elif status_code == 4:
                status = "failed"
            else:
                status = "in_progress"
            
            print(f"DEBUG: Asset {art_id} type={type_code} status={status_code}")
            
            url = None
            if asset_type == "audio" and len(art) > 6 and isinstance(art[6], list) and len(art[6]) > 3:
                url = art[6][3]
            elif asset_type == "video" and len(art) > 8 and isinstance(art[8], list) and len(art[8]) > 3:
                url = art[8][3]
            elif asset_type == "infographic" and len(art) > 14 and isinstance(art[14], list) and len(art[14]) > 2:
                # url is at [14][2][0][1][0]
                try:
                    img_data = art[14][2]
                    if img_data and isinstance(img_data, list):
                        url = img_data[0][1][0]
                except (IndexError, TypeError):
                    pass
            elif asset_type == "slide_deck" and len(art) > 16 and isinstance(art[16], list) and len(art[16]) > 0:
                url = art[16][0]
            
            if url and not isinstance(url, str):
                url = str(url)

            assets.append(Asset(
                id=art_id,
                notebook_id=notebook_id,
                type=asset_type,
                status=status,
                url=url
            ))
            
        return assets

    def download_file(self, url: str, output_path: str):
        client = self._get_client()
        # Add specific headers for download if needed, but client already has cookies
        with client.stream("GET", url, follow_redirects=True) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

    def create_video_overview(
        self,
        notebook_id: str,
        source_ids: List[str],
        format_code: int = 1,  # VIDEO_FORMAT_EXPLAINER
        visual_style_code: int = 1,  # VIDEO_STYLE_AUTO_SELECT
        language: str = "it",
        focus_prompt: str = "",
    ) -> Dict:
        # Build source IDs in the nested format: [[[id1]], [[id2]], ...]
        sources_nested = [[[sid]] for sid in source_ids]

        # Build source IDs in the simpler format: [[id1], [id2], ...]
        sources_simple = [[sid] for sid in source_ids]

        video_options = [
            None, None,
            [
                sources_simple,
                language,
                focus_prompt,
                None,
                format_code,
                visual_style_code
            ]
        ]

        params = [
            [2],
            notebook_id,
            [
                None, None,
                3,  # STUDIO_TYPE_VIDEO
                sources_nested,
                None, None, None, None,
                video_options
            ]
        ]

        return self._call_rpc(self.RPC_CREATE_STUDIO, params)

    def create_infographic(
        self,
        notebook_id: str,
        source_ids: List[str],
        orientation_code: int = 3,  # INFOGRAPHIC_ORIENTATION_SQUARE
        detail_level_code: int = 3,  # INFOGRAPHIC_DETAIL_DETAILED
        language: str = "it",
        focus_prompt: str = "",
    ) -> Dict:
        # Build source IDs in the nested format: [[[id1]], [[id2]], ...]
        sources_nested = [[[sid]] for sid in source_ids]

        infographic_options = [[focus_prompt or None, language, None, orientation_code, detail_level_code]]

        content = [
            None, None,
            7,  # STUDIO_TYPE_INFOGRAPHIC
            sources_nested,
            None, None, None, None, None, None, None, None, None, None,  # 10 nulls
            infographic_options
        ]

        params = [
            [2],
            notebook_id,
            content
        ]

        return self._call_rpc(self.RPC_CREATE_STUDIO, params)

    def get_notebook_sources(self, notebook_id: str) -> List[Source]:
        result = self.get_notebook_details(notebook_id)
        sources = []
        if result and isinstance(result, list) and len(result) >= 1:
            notebook_data = result[0] if isinstance(result[0], list) else result
            sources_data = notebook_data[1] if len(notebook_data) > 1 else []
            if isinstance(sources_data, list):
                for src in sources_data:
                    if isinstance(src, list) and len(src) >= 3:
                        source_id = src[0][0] if src[0] and isinstance(src[0], list) else None
                        title = src[1] if len(src) > 1 else "Untitled"
                        metadata = src[2] if len(src) > 2 else []
                        
                        source_type = "unknown"
                        if isinstance(metadata, list) and len(metadata) > 4:
                            type_code = metadata[4]
                            type_map = {
                                1: "google_docs",
                                2: "google_slides_sheets",
                                3: "pdf",
                                4: "pasted_text",
                                5: "web_page",
                                8: "generated_text",
                                9: "youtube",
                                11: "uploaded_file",
                                13: "image",
                                14: "word_doc"
                            }
                            source_type = type_map.get(type_code, "unknown")

                        if source_id:
                            sources.append(Source(
                                id=source_id,
                                notebook_id=notebook_id,
                                title=title,
                                type=source_type,
                                char_count=0
                            ))
        return sources


