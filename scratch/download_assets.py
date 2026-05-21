
import json
import os

# Data from notebooklm-mcp-auth --show-tokens
tokens = {
  "cookies": {
    "__Secure-1PAPISID": "0mEmVPYdm6Kv_oKO/ARTsjGo9R_nfam1Ef",
    "_ga": "GA1.1.283143641.1777385322",
    "SID": "g.a0008ggEwy4r6OjWghD1lNNwa6ZdYnhumfvDuizJX4SEdeD4Oq4u9LOqIig8O4BtlCK_JdlP0QACgYKASQSARUSFQHGX2Mi4TgSanrOWFABgF60aY42QxoVAUF8yKqQcbC8843GSeIJbbFCEGXV0076",
    "__Secure-1PSID": "g.a0008ggEwy4r6OjWghD1lNNwa6ZdYnhumfvDuizJX4SEdeD4Oq4u0Gliww-p4x6mH8Sv1eQJdgACgYKAb0SARUSFQHGX2MiBe0NPvXqMuN-IWPExZbRtBoVAUF8yKrZ-3w_s4OwMkkZxawlPIhD0076",
    "OSID": "g.a0008ggEw9_PEvyN7CIBG6bbeUoirRNc-fEeiCqPr-XkvE6FjRR3INlm4DfmapaPVop4asFAtwACgYKAU0SARUSFQHGX2MiNS9FVl4fc0oh4dLDrQ-iGRoVAUF8yKqDLgkLv48s24N6AFKeFP-V0076",
    "SAPISID": "0mEmVPYdm6Kv_oKO/ARTsjGo9R_nfam1Ef",
    "__Secure-1PSIDTS": "sidts-CjIBhkeRdyccD44VxJbzjG7cW2pJ4rOlSPlksDmJbBXSpQtudOcUOjTsoOiKrPklwKyZCBAA",
    "__Host-GAPS": "1:eCcGC5CK1kEqm5o_3Svtuu-EC7KzUM5c4UXwZ74r59NXhVX8F5sgbLWC3m_xEiccIUYWsctSi7cQZ0tzOMGJjEIGV8K9kA:k0CsIn8RCLSqaITj",
    "HSID": "A8vF4_l9Mfo6PzygB",
    "__Secure-3PSIDCC": "AKEyXzUpHcdpeuVAlxfvAbPzHz7ryU8CaVBGZlqeliJ9WeG_Ie0jqUmiB3Xnskao3v2LFEybKQ",
    "NID": "531=j3SLxh6msTnhnJod5J-XZC0lV81CC8PMPkkHZp3Sz1IIsdzfKKow5tda3oZHLTzgK8sKJ1hnUmk6AIC4oYSCnoko_IRfGQ_bGBIh5zCu0L7S5kr9LPY5WFyQOme2eTl43bdDFm6C1l05yvvVF5AmMRqHAK5Xj19R8ivo8NrUziNgRO_fHoEThXiDsL95fp8g5FD48T18oyOglpqSdGZ8GysC_986X-_QbjJ3h_z7uw0yYWai-SlYf8Ab3xSbTFhmOT_yeOvTG6mPocGQhHveyqd4X7Ed1bDmZ5w6iHc5WuH0URKEdN7UNkuFMxCZYrIpxkeuzZGbRMZJhaAgVN640IR5-wSKoLfzD5ocPfRtuHcu-y1Z_SQicNJlHr0WRpLRMzZBNh7WYNJNB9TKNLkkJBoWd_sXJGmiEsupTQvVxLUHlHYtGCm6UGkk8JOSZDP3xkm0nRiVaobJgoCNpmc-esUJY2f0wjdttz8iaxW3cXRhnYXDfLz5QPJBN-zxO2toDtZRRCoeJQIjTpw7QWjw7XHO7EoBMuE7_9BF6Vi_XNL8fcwLl-pEAEsguPKGODO0WUPUuyw0f8eOYR5ssdx6LE1y7rdnN49PTPqM6jYG-DMK-_pdhoxqcT41shNlx2IQJmGT3jbrPFfvdtsu97xKtKCI-e0BoBK7uKokCKIthN01bKwSTJB_In6XUvUdT4fSGu9pw4Au4c_OolOZJoYb",
    "_gcl_au": "1.1.1663430872.1777385321",
    "SSID": "AXD-rErjH9p5IR_IF",
    "_ga_W0LDH41ZCB": "GS2.1.s1777385321$o1$g0$t1777385323$j58$l0$h0",
    "__Secure-ENID": "33.SE=BZKvzI5wzhxPvLJTGv85m1M33xUrrbdi-EqSc44CBqTKi7btalNVy9lBewIGHBYbTW_LfoViF9Cpi8XVJf968_Z-Mx6MPnis5nhqpxdf7fEdB1c68LhOfKGhCQMO_GwvdZPizrITAy2WRQTj8B2vqwgWk1SBFy2ADtprieu2F3Z5JZ6qJGDMWInZRqavaf-9qz1pMUPQEr6aRlaaI0_TeneGzrVSln9sUHcX-xW2ylJ2S6jF0JXnvp4WRvo6wKbQVjaVrq9XSM361zBtcezMX3CL45ay",
    "SIDCC": "AKEyXzXXqz9k8iGbBtOxyCpKM9G7s7Mv4QIReKQO8xwKpMn66lWTqYvB8TYNJ9oM00mjUDAKvg",
    "__Secure-1PSIDCC": "AKEyXzWuA6aIa9Irle8svzXXePddxkYsVAQTZXFKG2loWqQxXB67xjD1_C3Ok6e3CjOg4rRC",
    "__Secure-3PAPISID": "0mEmVPYdm6Kv_oKO/ARTsjGo9R_nfam1Ef",
    "LSID": "o.notebooklm.google.com|s.IT|s.youtube:g.a0008ggEw5d4YqUGwHXA2KPd2J5My9OoQmrzQhG8j_m2GCa2fS1PelN7qJHrB9BFpF0sZQ8KOgACgYKASMSARUSFQHGX2Mi32FrA3zoEu2ZscJhJU9ayhoVAUF8yKpbGxsjjKUmvaJoLq7a1w6a0076",
    "__Host-3PLSID": "o.notebooklm.google.com|s.IT|s.youtube:g.a0008ggEw5d4YqUGwHXA2KPd2J5My9OoQmrzQhG8j_m2GCa2fS1Pkx4qA0IWIoSYMIg4SdwwPgACgYKAUISARUSFQHGX2MiyPbHWtE5phgIP624YwD3IBoVAUF8yKqwSGtC2bYvwFZpp43lQ6Pj0076",
    "APISID": "SbuNN-Jwf07NYPf3/AJ_szZBBgALXbNa4T",
    "__Secure-OSID": "g.a0008ggEw9_PEvyN7CIBG6bbeUoirRNc-fEeiCqPr-XkvE6FjRR3Ws36OsGyMt5chwmc_Lz0ZwACgYKAeoSARUSFQHGX2MiwnnQewpg_k1aIikXXIHlVhoVAUF8yKrBdXgz5jAHKpVj5pVj7_kX0076",
    "__Secure-3PSID": "g.a0008ggEwy4r6OjWghD1lNNwa6ZdYnhumfvDuizJX4SEdeD4Oq4uP1lls8Q3RoUaDgrzd-haFQACgYKAWQSARUSFQHGX2MinOkUrKdKTn282LN6uiK35RoVAUF8yKoG8Y3EllMzo3TPjiBjkHB40076",
    "__Host-1PLSID": "o.notebooklm.google.com|s.IT|s.youtube:g.a0008ggEw5d4YqUGwHXA2KPd2J5My9OoQmrzQhG8j_m2GCa2fS1Pp0DgQNvOZlezll8F1rVPcwACgYKAQkSARUSFQHGX2Miy4iWpSE7_edrkeiCppuXqBoVAUF8yKo3K9px3uMfdmaq2FRb8Ajg0076",
    "__Secure-3PSIDTS": "sidts-CjIBhkeRdyccD44VxJbzjG7cW2pJ4rOlSPlksDmJbBXSpQtudOcUOjTsoOiKrPklwKyZCBAA",
    "OTZ": "8551583_48_52_123900_48_436380",
    "ACCOUNT_CHOOSER": "AFx_qI6LN9BEoBVzo4ZdAxm2lQ8rmlFVYFWnXoSbXxWB7xhkeBbFsdtcjT9UEXUxO8-HKSFaC0x5Z27UTpFO06m0PPLjwMLeroLIxQTy0UfitINQOOH5gfqgOIeJwL5yYwNISCnOlcn4qrCXXG1PaC7hbHQ6-JbcFQ"
  }
}

cookies_dict = tokens["cookies"]
cookie_str = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])

# Infographic URL from studio_status
info_url = "https://lh3.googleusercontent.com/notebooklm/AKXwDQGDpYr30j5vYogkYCAkrjQFxugbybUPsj64TY7QSVc2fRFDyQSoWIHTnS_cMYqQ4loAJw3hGwW78UtK9wMeso9HZRX9q339-p5asUrSWDO5aa-fhEKc-_NydnCigP94D33knhV0bodRHHXL31sP1pksMZHbs28=w2048-d-h2048-mp2"
# Video URL from studio_status
video_url = "https://lh3.googleusercontent.com/notebooklm/AKXwDQG3wAraCbWLo--YWISXlrt51xiv_oAIDxjcyzjANIeRFK7HUO7WfOJVWTsWUMwYYEOrgPQkVDwH6z1_9kKtgL4SIrMmSpQNmInN8WeFt4vNams7bmf4xcw7pXxm8A4oormL_uwgDIjmnnQSWACsTNMl1jHAYVs=m22-dv"

downloads = [
    (info_url, os.path.expanduser("~/Downloads/infografica_raw.png")),
    (video_url, os.path.expanduser("~/Downloads/video_raw.mp4"))
]

for url, output in downloads:
    cmd = f'python3 /Users/marcolemoglie_1_2/Desktop/canale/Execution/enea/notebooklm_asset_downloader.py --url "{url}" --output "{output}" --cookies "{cookie_str}"'
    print(f"Executing: {cmd}")
    os.system(cmd)
