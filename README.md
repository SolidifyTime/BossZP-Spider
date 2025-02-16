# Boss直聘爬虫项目

## 项目简介
这是一个基于Selenium的Boss直聘网站爬虫项目，用于抓取深圳地区的职位信息。该爬虫采用了多种反爬虫策略，支持代理IP配置，并能够稳定地获取职位数据。

## 功能特点
- 自动处理反爬虫机制，模拟真实浏览器行为
- 支持代理IP配置，提高爬取成功率
- 数据自动保存为CSV格式，支持Excel直接打开
- 完善的异常处理和日志记录机制
- 支持自定义搜索关键词和爬取页数

### 开发环境
- 操作系统：macOS Sonoma
- Python版本：3.9
- Chrome浏览器版本：133.0.6943.98

### 依赖要求
- Python 3.6+
- Chrome浏览器
- ChromeDriver（与Chrome浏览器版本匹配）
- MySQL 5.7+（可选，如需使用数据库存储）

## 依赖安装
```bash
pip install -r requirements.txt
```

## MySQL数据库配置
1. 下载安装MySQL
   - Windows用户：访问[MySQL官网](https://dev.mysql.com/downloads/mysql/)下载安装包
   - Mac用户：使用Homebrew安装
     ```bash
     brew install mysql
     ```
   - Linux用户：
     ```bash
     sudo apt-get install mysql-server  # Ubuntu/Debian
     sudo yum install mysql-server      # CentOS/RHEL
     ```

2. 启动MySQL服务
   - Windows：在服务管理器中启动MySQL服务
   - Mac/Linux：
     ```bash
     sudo service mysql start  # Linux
     brew services start mysql # Mac
     ```

3. 设置root密码
   ```bash
   mysql_secure_installation
   ```
   按照提示设置root密码并完成安全配置

4. 创建数据库和表
   ```sql
   mysql -u root -p
   CREATE DATABASE boss_spider DEFAULT CHARACTER SET utf8mb4;
   USE boss_spider;
   CREATE TABLE jobs (
       id INT AUTO_INCREMENT PRIMARY KEY,
       position VARCHAR(100),
       salary VARCHAR(50),
       company VARCHAR(100),
       job_type VARCHAR(50),
       details TEXT,
       create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
   ```

## 配置说明
在`config.yaml`文件中可以配置以下参数：
- 爬虫并发数
- 请求超时时间
- 请求间隔
- 重试次数
- 最大爬取页数
- 代理服务器配置

### 获取Headers和Cookies
1. 打开Chrome浏览器，访问Boss直聘网站
2. 按F12打开开发者工具，切换到Network标签
3. 在网页上进行一次搜索操作
4. 在Network面板中找到搜索请求（通常是job相关的请求）
5. 右键请求，选择"Copy > Copy as cURL (bash)"
6. 从cURL命令中提取headers和cookies信息

示例headers配置：
```yaml
headers:
  accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
  accept-encoding: "gzip, deflate, br"
  accept-language: "zh-CN,zh;q=0.9,en;q=0.8"
  user-agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
```

## 使用方法
1. 克隆项目到本地
```bash
git clone [项目地址]
cd bosszp_Trae
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置config.yaml
根据需要修改配置文件中的参数

4. 运行爬虫
```bash
python spider.py
```

5. 按区域检索（可选）
如果需要按区域检索职位信息，只需修改spider.py中的search_url变量，在URL后添加区域参数即可。例如：
- 福田区：`https://www.zhipin.com/web/geek/job?query={keyword}&city=101280600&district=1000&subdistrict=1000100`
- 南山区：`https://www.zhipin.com/web/geek/job?query={keyword}&city=101280600&district=2000&subdistrict=2000100`

如果需要爬取其他城市的数据，只需修改URL中的city参数即可。常见城市的city参数值：
- 北京：101010100
- 上海：101020100
- 广州：101280100
- 深圳：101280600
- 杭州：101210100
- 成都：101270100

例如，爬取北京地区的职位信息：
`https://www.zhipin.com/web/geek/job?query={keyword}&city=101010100`

## 数据格式
爬取的数据将保存为CSV格式，包含以下字段：
- position: 职位名称
- salary: 薪资范围
- company: 公司名称
- job_type: 职位类型
- details: 职位详情

## 注意事项
- 请遵守网站的robots协议
- 建议适当设置请求间隔，避免频繁请求
- 使用代理IP时，请确保代理服务器的稳定性
- 首次运行前请确保已正确配置Chrome浏览器和ChromeDriver

## 更新日志
### v1.0.0
- 实现基础爬虫功能
- 添加代理支持和反爬虫措施
- 实现数据导出为CSV格式

## 许可证
MIT License

## 贡献指南
欢迎提交Issue和Pull Request来帮助改进项目。

## 联系方式
如有问题，请提交Issue或联系项目维护者。
