from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from loguru import logger
import time
import csv
import yaml
import random
from fake_useragent import UserAgent
from retrying import retry
import requests

class BossSpider:
    def __init__(self, config_path='config.yaml'):
        """初始化爬虫"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.driver = None
        self.wait = None
        self.proxy = None
        if self.config['proxy']['enable']:
            self._update_proxy()

    def _update_proxy(self):
        """获取新的代理IP"""
        try:
            response = requests.get(self.config['proxy']['api'])
            if response.status_code == 200:
                self.proxy = response.text.strip()
                logger.info(f"成功更新代理IP: {self.proxy}")
            else:
                logger.warning("获取代理IP失败，将使用直接连接")
        except Exception as e:
            logger.error(f"获取代理IP出错: {str(e)}")

    @retry(stop_max_attempt_number=3, wait_random_min=2000, wait_random_max=5000)
    def _init_driver(self):
        """初始化Chrome浏览器"""
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument(f'user-agent={UserAgent().random}')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--disable-web-security')
        options.add_argument('--start-maximized')
        options.add_argument('--ignore-certificate-errors')

        # 添加代理支持
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')

        # 添加更多的浏览器指纹模拟
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        prefs = {
            'profile.default_content_setting_values': {
                'notifications': 2,
                'images': 2
            },
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False
        }
        options.add_experimental_option('prefs', prefs)

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.navigator.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [
                    {name: 'Chrome PDF Plugin'}, 
                    {name: 'Chrome PDF Viewer'}, 
                    {name: 'Native Client'}
                ]});
                Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'});
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            '''
        })
        self.wait = WebDriverWait(self.driver, 20)

    @retry(stop_max_attempt_number=3, wait_random_min=5000, wait_random_max=10000)
    def search_jobs(self, keyword):
        """搜索职位"""
        if not self.driver:
            self._init_driver()

        try:
            # 构建搜索URL
            search_url = f"https://www.zhipin.com/web/geek/job?query={keyword}&city=101280600"
            self.driver.get(search_url)
            time.sleep(random.uniform(8, 12))  # 增加初始等待时间

            # 开始爬取数据
            self._crawl_jobs(keyword)

        except Exception as e:
            logger.error(f"搜索职位失败: {str(e)}")
            # 添加截图功能以便调试
            try:
                self.driver.save_screenshot(f'error_{time.strftime("%Y%m%d_%H%M%S")}.png')
            except:
                pass
            # 如果是代理问题，尝试更新代理
            if 'Connection reset by peer' in str(e) and self.config['proxy']['enable']:
                self._update_proxy()
                raise  # 触发重试机制
        finally:
            if self.driver:
                self.driver.quit()

    def _crawl_jobs(self, keyword):
        """爬取职位信息"""
        page = 1
        while page <= self.config['spider']['max_pages']:
            try:
                # 随机延迟，模拟人类行为
                time.sleep(random.uniform(3, 5))  # 增加等待时间
                
                # 等待页面加载完成，增加重试次数和超时时间
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        # 等待任一元素出现，使用presence_of_all_elements_located替代
                        elements = self.wait.until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'job-card-wrapper'))
                        )
                        if not elements:
                            elements = self.wait.until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, 'job-list'))
                            )
                        # 确保页面完全加载
                        time.sleep(random.uniform(2, 3))
                        break
                    except Exception as e:
                        if retry == max_retries - 1:
                            raise Exception(f"页面加载超时: {str(e)}")
                        time.sleep(random.uniform(2, 3))
                
                # 随机滚动页面，增加滚动次数和间隔
                for _ in range(4):
                    scroll_height = random.randint(300, 800)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                    time.sleep(random.uniform(0.8, 1.8))
                
                # 滚动到底部并等待加载
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 3))

                # 使用显式等待获取职位信息
                get_element_texts = lambda xpath: [
                    element.text for element in self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, xpath))
                    )
                ]
                
                # 分步获取数据并验证
                jobs = get_element_texts('//span[@class="job-name"]')
                if not jobs:
                    raise Exception("未找到职位名称数据")
                    
                salaries = get_element_texts('//span[@class="salary"]')
                companies = get_element_texts('//h3[@class="company-name"]/a')
                job_types = get_element_texts('//div[contains(@class, "job-card-footer")]//li[1]')
                
                # 使用显式等待获取详情
                details = self.wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'info-desc'))
                )
                details = [detail.text for detail in details]

                # 验证数据完整性和一致性
                data_lengths = [len(x) for x in [jobs, salaries, companies]]
                if not all(x == data_lengths[0] for x in data_lengths):
                    logger.warning(f"关键数据长度不一致，尝试重新获取: jobs={len(jobs)}, salaries={len(salaries)}, "
                                f"companies={len(companies)}")
                    time.sleep(random.uniform(3, 4))  # 增加等待时间
                    continue

                # 对于非关键字段，使用现有长度
                job_types = job_types[:len(jobs)] if job_types else [""] * len(jobs)
                details = details[:len(jobs)] if details else [""] * len(jobs)

                # 保存数据
                self._save_data(keyword, jobs, salaries, companies, job_types, details)
                logger.info(f"已完成第{page}页数据爬取，获取到{len(jobs)}条职位信息")

                # 优化翻页逻辑
                time.sleep(random.uniform(2, 3))
                try:
                    # 使用显式等待查找下一页按钮
                    next_button = self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'ui-icon-arrow-right'))
                    )
                    
                    # 检查是否为最后一页
                    if 'disabled' in next_button.get_attribute('class'):
                        logger.info("已到达最后一页")
                        return
                        
                    # 确保按钮可点击
                    self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'ui-icon-arrow-right')))
                    self.driver.execute_script("arguments[0].click();", next_button)
                    page += 1
                    # 翻页后额外等待
                    time.sleep(random.uniform(3, 4))
                except Exception as e:
                    logger.error(f"翻页失败: {e}")
                    break

            except Exception as e:
                logger.error(f"爬取第{page}页数据失败: {e}")
                # 截图记录错误状态
                try:
                    self.driver.save_screenshot(f'error_page_{page}_{time.strftime("%Y%m%d_%H%M%S")}.png')
                except:
                    pass
                break

    def _save_data(self, keyword, jobs, salaries, companies, job_types, details):
        """保存职位数据"""
        data = []
        for i in range(len(jobs)):
            try:
                # 获取并清理数据，添加更多的错误处理
                position = jobs[i].strip() if i < len(jobs) else '未知职位'
                salary = salaries[i].strip() if i < len(salaries) else '薪资面议'
                company = companies[i].strip() if i < len(companies) else '未知公司'
                job_type = job_types[i].strip() if i < len(job_types) else ''
                detail = details[i].strip() if i < len(details) else ''
                
                # 放宽数据验证条件，只要职位名称存在即可
                if not position or position == '未知职位':
                    logger.warning(f"第{i+1}条数据职位名称缺失，跳过")
                    continue
                    
                job_info = {
                    'position': position,
                    'salary': salary,
                    'company': company,
                    'job_type': job_type,
                    'details': detail
                }
                data.append(job_info)
                logger.debug(f"成功处理第{i+1}条数据: {position}")
            except Exception as e:
                logger.error(f"处理第{i+1}条职位数据失败: {e}")
                continue

        # 保存到CSV文件，确保使用UTF-8编码并添加BOM
        csv_file = f'深圳{keyword}_jobs.csv'
        try:
            # 使用UTF-8-SIG编码（带BOM），这样Excel打开时不会乱码
            with open(csv_file, mode='a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['position', 'salary', 'company', 'job_type', 'details'])
                if f.tell() == 0:  # 如果文件为空，写入表头
                    writer.writeheader()
                writer.writerows(data)
            logger.info(f"数据已保存到{csv_file}，本次保存{len(data)}条数据")
        except Exception as e:
            logger.error(f"保存数据到CSV文件失败: {e}")

if __name__ == '__main__':
    # 配置日志
    logger.add('spider_{time}.log', rotation='1 day', retention='7 days')
    
    # 实例化爬虫并启动
    spider = BossSpider()
    spider.search_jobs('销售')