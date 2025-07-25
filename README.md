# TaaP POC GitHub

## 项目简介

这是一个基于Tekton云原生测试平台的概念验证（POC）项目。该项目包含300个不同的pytest测试用例，涵盖了云原生环境下的各种测试场景，为将来在Tekton平台上的差异化表现做准备。

## 项目特点

- **300个差异化测试用例**：与GitLab版本有差异，确保在Tekton上有不同的表现
- **云原生架构**：支持Docker、Kubernetes、数据库、API等多种技术栈
- **最佳实践**：遵循pytest最佳实践，包含完整的测试覆盖率和报告
- **模块化设计**：清晰的代码结构，便于维护和扩展

## 测试用例分布

| 测试类别 | 数量 | 说明 |
|----------|------|------|
| API端点测试 | 80个 | 用户、产品、订单、认证相关的API测试 |
| 容器操作测试 | 60个 | Docker和Kubernetes容器管理测试 |
| 数据库操作测试 | 50个 | PostgreSQL和MongoDB数据库测试 |
| 配置管理测试 | 40个 | 配置加载、验证、环境变量等测试 |
| 网络和安全测试 | 55个 | 网络连接、SSL/TLS、加密、安全防护测试 |
| 性能监控测试 | 15个 | 性能指标、负载测试、资源监控测试 |
| **总计** | **300个** | 涵盖云原生应用的各个方面 |

## 项目结构

```
TaaP_POC_github/
├── README.md                          # 项目说明文档
├── requirements.txt                    # Python依赖包
├── pytest.ini                        # pytest配置文件
├── conftest.py                        # pytest全局配置和fixture
├── .gitignore                         # Git忽略文件
├── src/                               # 源代码目录
│   ├── __init__.py
│   ├── config.py                      # 配置管理
│   ├── database.py                    # 数据库管理
│   ├── api_client.py                  # API客户端
│   └── container_manager.py           # 容器管理
└── tests/                             # 测试用例目录
    ├── __init__.py
    ├── test_api_endpoints.py           # API端点测试 (80个)
    ├── test_container_operations.py    # 容器操作测试 (60个)
    ├── test_database_operations.py     # 数据库操作测试 (50个)
    ├── test_configuration_management.py # 配置管理测试 (40个)
    ├── test_network_security.py        # 网络安全测试 (55个)
    └── test_performance_monitoring.py  # 性能监控测试 (15个)
```

## 快速开始

### 1. 环境准备

确保您的系统已安装以下软件：
- Python 3.8+
- pip (Python包管理器)

### 2. 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd TaaP_POC_github

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定类别的测试
pytest -m api           # API测试
pytest -m container     # 容器测试
pytest -m database      # 数据库测试
pytest -m unit          # 单元测试
pytest -m integration   # 集成测试
pytest -m security      # 安全测试
pytest -m performance   # 性能测试

# 运行特定测试文件
pytest tests/test_api_endpoints.py
pytest tests/test_container_operations.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 生成详细的HTML报告
pytest --html=reports/report.html --self-contained-html

# 并行运行测试（加速）
pytest -n auto  # 使用所有CPU核心
pytest -n 4     # 使用4个进程
```

### 4. 查看测试报告

测试完成后，您可以在以下位置查看报告：
- HTML测试报告：`reports/report.html`
- 覆盖率报告：`reports/coverage/index.html`

## 配置选项

### 环境变量配置

您可以通过环境变量自定义配置：

```bash
# 数据库配置
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=taap_db
export DB_USER=taap_user
export DB_PASSWORD=your_password

# Redis配置
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=your_redis_password

# API配置
export API_BASE_URL=http://localhost:8080
export API_AUTH_TOKEN=your_auth_token

# Kubernetes配置
export KUBECONFIG=/path/to/kubeconfig
export K8S_NAMESPACE=default
```

### YAML配置文件

您也可以创建配置文件 `config.yaml`：

```yaml
database:
  host: localhost
  port: 5432
  name: taap_db
  user: taap_user
  password: your_password

redis:
  host: localhost
  port: 6379
  password: your_redis_password

api:
  base_url: http://localhost:8080
  timeout: 30
  retries: 3

container:
  docker_host: unix://var/run/docker.sock
  k8s_config_path: ~/.kube/config
  namespace: default

monitoring:
  prometheus_url: http://localhost:9090
  grafana_url: http://localhost:3000
  log_level: INFO
```

## 测试标记说明

测试用例使用pytest标记进行分类：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.api` - API测试
- `@pytest.mark.database` - 数据库测试
- `@pytest.mark.container` - 容器测试
- `@pytest.mark.network` - 网络测试
- `@pytest.mark.security` - 安全测试
- `@pytest.mark.performance` - 性能测试
- `@pytest.mark.slow` - 慢速测试

## CI/CD集成

### GitHub Actions示例

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Tekton Pipeline示例

```yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: taap-test-pipeline
spec:
  params:
  - name: git-url
    type: string
  - name: git-revision
    type: string
    default: main
  
  tasks:
  - name: git-clone
    taskRef:
      name: git-clone
    params:
    - name: url
      value: $(params.git-url)
    - name: revision
      value: $(params.git-revision)
  
  - name: run-tests
    runAfter: [git-clone]
    taskSpec:
      steps:
      - name: install-deps
        image: python:3.10
        script: |
          cd $(workspaces.source.path)
          pip install -r requirements.txt
      
      - name: run-pytest
        image: python:3.10
        script: |
          cd $(workspaces.source.path)
          pytest --junitxml=test-results.xml --cov=src
      
      - name: generate-reports
        image: python:3.10
        script: |
          cd $(workspaces.source.path)
          pytest --html=reports/report.html --self-contained-html
    
    workspaces:
    - name: source
      workspace: shared-data
  
  workspaces:
  - name: shared-data
```

## 故障排除

### 常见问题

1. **导入错误**：确保已安装所有依赖包
   ```bash
   pip install -r requirements.txt
   ```

2. **Docker连接失败**：确保Docker服务正在运行
   ```bash
   sudo systemctl start docker
   ```

3. **Kubernetes配置错误**：检查kubeconfig文件
   ```bash
   kubectl config view
   ```

4. **测试超时**：增加测试超时时间
   ```bash
   pytest --timeout=300
   ```

### 调试测试

```bash
# 详细输出
pytest -v -s

# 调试特定测试
pytest tests/test_api_endpoints.py::TestUserAPIEndpoints::test_get_user_success -v -s

# 进入调试模式
pytest --pdb
```

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请联系：
- 项目维护者：TaaP POC Team
- 邮箱：taap-poc@example.com
- 问题跟踪：[GitHub Issues](https://github.com/your-org/TaaP_POC_github/issues)

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 包含300个差异化测试用例
- 支持多种云原生技术栈
- 完整的CI/CD集成示例