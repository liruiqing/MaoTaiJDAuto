import sys
from jd_mask_spider_requests import Jd_Mask_Spider

if __name__ == '__main__':
    start_tool = Jd_Mask_Spider()
    start_tool.login()
    start_tool.make_reserve()
