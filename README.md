# Format HTML to python object

Support xpath

# Sample config

```
ep_conf = {"url": "{{video_url}}",
            "root": "{{root}}",
            "items": "//div[@class=\"container\"]/div[2]/div/div[@class=\"myui-panel-bg\"]/div/div[2]/div[@id=\"playlist{{st_cde}}\"]/ul/li[*]/a",
            #    "items": "//div[@class=\"myui-panel-bg\"]/div/div[@class=\"tab-content\"]/div[@id=\"playlist{{st_cde}}\"]/ul/li[*]/a",
            "data": {"root": {"fix": "{{root}}"},
                    "menu_desc": {"fix": "{{menu_desc}}"},
                    "smenu_desc": {"fix": "{{smenu_desc}}"},
                    "video_desc": {"fix": "{{video_desc}}"},
                    "video_img": {"fix": "{{video_img}}"},
                    "st_cde": {"fix": "{{st_cde}}"},
                    "st_desc": {"fix": "{{st_desc}}"},
                    "ep_cde": {"_attr": "href", "_act": [{"split": {"-": 3}}, {"re": ".html$"}, {"check": {"type": "int"}}]},
                    "ep_url": {"_attr": "href", "_act": [{"pfx": "{{root}}"}]},
                    "ep_desc": {"get": "_text"}
                    }}
```

# Execution

```
import html2obj
ext = html2obj.extract()
obj = ext.extract(conf=ep_conf)
```
