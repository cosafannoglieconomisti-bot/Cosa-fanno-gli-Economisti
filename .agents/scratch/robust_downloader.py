import requests
import os

# MCP Cookies
COOKIES = "OSID=g.a0009wg3jAqDvJGs1gPUPmthP0liLDTmt_LCnHDlhuy9fnKSHPiKzgMDUmYp2o6FZSW9juGprwACgYKAYgSARISFQHGX2Mi-T22p8cW1ksukytT24twsBoVAUF8yKqjPTvMWRTO4K8mn-YGTPc70076; LSID=o.mail.google.com|o.notebooklm.google.com|s.IT|s.youtube:g.a0009wg3jOwQ0_GBdq3NQNAjMYqTidprGbgMcvfcFblL6Frat6_JOBVzXFr5ciqONSONkVjsjwACgYKAYsSARISFQHGX2Mi8FvqJx52R9chFjs5lrLVMhoVAUF8yKoHucRFaKLHqj_6XVq3lvmf0076; __Secure-1PSIDCC=AKEyXzUUc_sJl9oU8RcTAHz9Af7fuvqAuWKE-IliVVRRBSbftOHMMxoSGa6OvFSlcPegi5n8; _gcl_au=1.1.1663430872.1777385321; __Secure-3PSIDCC=AKEyXzUpwBNRzTpHbVRFN05Z9Ho-W4Bdaa6y5xk8O4NPcaJig1tXb07MVxYN1WZ3zZtt7dwk9Q; NID=531=VNbNs7vNJVv4V5bva5i13xlpKmgagNLpORa0Zob5iMyVWipJHndnxXdJvM97UeEW1gAow4rQYnVnPsfI5vsiZxIhBJJqrEMEGOdoaz0niTNt-wUYyuXf85o2EMKyEcrz-XQ6fTVJD0a9gq1U8L037XuA22fywAmsJTr8nD5ApEVca6c-nVuMd9D7NtEaXJ5HM3UCr9lwmgnB4SzwdH4DviY-fnhAWefvpcYiyOqWKxGziNIZ53trnYaRh90THF9NR1Ojwob7vL7grIGMnvIDVIYDtEqXZyXucroY7kBdP0YMOMyijZ-dDerYNQq141Dkt75ZCRXs-STvH-34B79UrY49a0EORdFTRReUug3JkN2iWHr0rD_44cMPhPjaoi1klAx0JDUEJ27XDdLbp22rcSa3tsvA-bZAQeULsEjdlx3r797tO3e8VTcl-phEzwsvaAOSvgZ-UzjS_FkKSRFM1RixLMDQi2ytmtvPFAecqgg_xaqfUdOYeqW1bAVxQXmsRZEkhM_6fEWyvwhM9Osu32JBKI0OmyaeL6lKn5cWt-tGz86e9iGXyMbshzQeZ67mv7n1Yr44b4zK2rUFg5l8AAxrwNAYI96ZaEWJKqvOVoGt_ikKU5fv2PRib_wyleYEbDyqeVV6uj4QuJaJiuE_35EFPpE5nLHsqSlX59OiJZtbPIFieDp_nROMB1rI-_4UP7-17gc52g5BNZB5iMejUf5Q6U7KpdTCKpPPvG8MqkKFEVGcF9ljJrxZy6YVqcRi8wI52cXcGcf4jQ7F_5TLmu9hiUBFZl_xHHVj68tkQzePOT9ezocuyp7gFbC9PR7hhXVihwGIzv9ki-L7DNUSK2nrgIpsV13VoHSMop94ri_wsFUI0zN9Nu3l4RSU3jsRj8m45PbiQeQEj6UihYIq5TnPlTGsVtvvp0JQTK96XdS-A-p_GZVmhm8VioaheHYTYpTbWcLHhvFVJRY7X6Yla5yZoR_NpslGo_h0nJixCHgS1P_8EdV3RqR7kkUWaV8kqXl89PCMoKi-dA; __Secure-ENID=33.SE=KA1KXhwwNNWrtlXMqFOnuXpc5Ks-yEsVzfs8_F3nWDK0mlZxHvVSAwPT_mKYL2QTVwhab929tPr44_kzi0epO32BLI7JnfDXPqpq1Wi4XkdlHDtbodOqWIkeN3L3rhw-D-ftyEQEfBkyqasG1Bb4Z6N40XX6kgXBll0XYHCUxwteE4BHeh3InObeMLP6e4BJCYc4f35f1iTScqnb01neC1UvQYlBoipE77ZOTjjXhfOM9Z6ct_Viqa5A6l3G-xoOrg-yjVF3sTjApJhKQqG79w256emWpPkiK00a8byFIzCui809vOt6GqPZGIEiRItkb9a3CGCzBrywVTkzmGVpbrqiDdvsCajzxl_mHXTD; SIDCC=AKEyXzVclWn3TlMm1L-NgvUP_uaFrDuJPps1TsFY971o0Vsu4FEZGMlqA2oBEld74lPLyt8PVQ; __Secure-1PSID=g.a0009wg3jF54RxI7SzB_ilOWWwwY4A5UIgV-KWvJuPncaGCZT1awz6OnAXfwQ4xBGIDopdp_eAACgYKAS0SARISFQHGX2MiOlcmVhzUXOmT_qM6X7JdGBoVAUF8yKofwl0pVh6J3pbs9u0gkLzB0076; _ga=GA1.1.283143641.1777385322; ACCOUNT_CHOOSER=AFx_qI6DxLt9EKxj39BYPbHvhLnIEPIK5jPJeEq6DqxbS6PBMWEFAJC5mErl6iDbT2zNRq1vSadt1o_zq4uBvFfXbcqMSU8CKf8oDT7SJiGCDJe87YXww2dQUcJEbgD7e-fpkEwhpfnrAWJYR_S9NCAbSjTFQPz-ttYNWWXYV2PorhAGD9bMHCKFSCuOeZH-Fa4Nmk6tpN1Hm7PfarHCEtZVSYq6rY3xtaGpaMqNz4b-02D_4rU7IGY; _ga_W0LDH41ZCB=GS2.1.s1778324925$o5$g1$t1778325377$j60$l0$h0; __Host-3PLSID=o.mail.google.com|o.notebooklm.google.com|s.IT|s.youtube:g.a0009wg3jOwQ0_GBdq3NQNAjMYqTidprGbgMcvfcFblL6Frat6_J6i3RZs2s49vR-n7fv8UhNAACgYKASISARISFQHGX2Mi7N__EP_wk84MfQoSzNpgAxoVAUF8yKoK1eO8NjaeTuSmOo6-277h0076; APISID=sxn3oEXmFPTNe-m0/Ac2fBZPhQ0jw0fjkg; __Secure-3PSIDTS=sidts-CjIBhkeRd5f4g2jbB3O3vVwwR7JnD9xKiJEatARipZJD4KfWiwoURNGUM8Q5m8zDL4zPvRAA; __Secure-OSID=g.a0009wg3jAqDvJGs1gPUPmthP0liLDTmt_LCnHDlhuy9fnKSHPiKPWNbXC8XTCJeWR6rH8kgTQACgYKARISARISFQHGX2Mi-qTNHy1EWlQokpGSi81y5RoVAUF8yKozEijcYjsT7MrvPKPGyUPY0076; __Secure-BUCKET=CN0H; __Host-1PLSID=o.mail.google.com|o.notebooklm.google.com|s.IT|s.youtube:g.a0009wg3jOwQ0_GBdq3NQNAjMYqTidprGbgMcvfcFblL6Frat6_JqT-4Moc2zp6lNyEAVnMqwgACgYKAWgSARISFQHGX2MixaYfIdcjMlLvOmES5WzLXxoVAUF8yKoS3bpPiG6C5kBF9RJCI_Xt0076; __Host-GAPS=1:z4Myaq0FfNKtCE5_L9wwCo4YGyKCURqc_UNP8Qck5BXBBkYdK3uczSjC3GeYG5lLXdOVCRxYJpSrPJBWZUuJNKdZNKBSmw:pVpg6PvUROj33OkG; __Secure-3PSID=g.a0009wg3jF54RxI7SzB_ilOWWwwY4A5UIgV-KWvJuPncaGCZT1awPfMFY-S3OeWdfapoRehdrAACgYKAYsSARISFQHGX2MifgMiGZxo7Dknpc_iIxlkxBoVAUF8yKr7ZplPvNlzH88DDkBbKOKp0076; __Secure-1PAPISID=6vnEOFWD8UumyHcp/AKfRxQmiT49R--qST; OTZ=8597766_48_52_123900_48_436380; HSID=AwC1N66aeClmYH00-; SSID=AvCy0L5dTeBd5rl80; __Secure-1PSIDTS=sidts-CjIBhkeRd5f4g2jbB3O3vVwwR7JnD9xKiJEatARipZJD4KfWiwoURNGUM8Q5m8zDL4zPvRAA; __Secure-3PAPISID=6vnEOFWD8UumyHcp/AKfRxQmiT49R--qST; AEC=AaJma5uu26osxVx-2qAD2FxE9WAhpX63wgI862s4i6l45woAH7QBbGz8gA; SID=g.a0009wg3jF54RxI7SzB_ilOWWwwY4A5UIgV-KWvJuPncaGCZT1aw2zip-mEwLg5OF_eKG1XlGQACgYKARASARISFQHGX2Miy22kWw0gWHAPmf7OobIARBoVAUF8yKpgi4GfjwjqGQQUyvPPt0rI0076; SEARCH_SAMESITE=CgQI5KAB; SAPISID=6vnEOFWD8UumyHcp/AKfRxQmiT49R--qST"

def download_asset(url, output_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': COOKIES,
        'Referer': 'https://notebooklm.google.com/',
        'Accept': '*/*',
    }
    
    print(f"Downloading from {url}...")
    response = requests.get(url, headers=headers, stream=True)
    
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type:
            print("Error: Received HTML instead of a binary file.")
            return False
            
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Success! Saved to {output_path}")
        return True
    else:
        print(f"Failed with status code: {response.status_code}")
        return False

if __name__ == "__main__":
    # Infographic URL (usually faster)
    info_lh3 = "https://lh3.googleusercontent.com/notebooklm/AKXwDQEMHTYAuTsdQ90l9VEh17CU9nXCLoHGf5oB9XRew2mmgD7vv2Q-nbuBoocsWPa3coqOI1jfb8tzy1TI4iObB06eVeGNv95JnRE2sgAEp69I46p5LAR5mAPCPTMFqW4cKfcVFOKgdbQJ4gYsZcGHOtwT5FV-OdA=w2048-d-h2048-mp2"
    
    print("--- Attempting Infographic Download ---")
    download_asset(info_lh3, "/Users/marcolemoglie_1_2/Downloads/Poveri_in_Pensione_infografica_raw.png")
