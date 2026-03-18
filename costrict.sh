#!/usr/bin/env bash
# =============================================================================
# costrict.sh — Costrict 部署管理入口脚本
# 用法: ./costrict.sh <command> [options]
# 命令:
#   check    — 检查环境依赖（docker、docker-compose 等）
#   prepare  — 准备部署环境（生成配置、解析模板等）
#   install  — 完整安装（prepare + 启动所有服务）
#   down     — 停止并移除所有容器
#   up       — 启动所有服务
# =============================================================================

# set -euo pipefail

# 脚本所在目录（绝对路径，兼容软链接调用）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载日志工具（颜色输出函数：info / success / warn / error / die）
# shellcheck source=scripts/logger/log_tool.sh
source "${SCRIPT_DIR}/scripts/logger/log_tool.sh"



# -----------------------------------------------------------------------------
# check — 检查运行环境
# -----------------------------------------------------------------------------
cmd_check() {
  info "开始检查运行环境..."

  local all_ok=true

  _check_cmd() {
    local cmd="$1"
    local min_ver="${2:-}"
    if command -v "${cmd}" &>/dev/null; then
      local ver
      ver="$(${cmd} --version 2>&1 | head -n1)"
      success "${cmd} 已安装：${ver}"
    else
      error "${cmd} 未找到，请先安装后再继续。"
      all_ok=false
    fi
  }

  _check_cmd docker
  if command -v docker-compose &>/dev/null; then
    local ver
    ver="$(docker-compose --version 2>&1 | head -n1)"
    success "docker-compose 已安装：${ver}"
  elif docker compose version &>/dev/null 2>&1; then
    success "docker compose 插件可用：$(docker compose version 2>&1 | head -n1)"
  else
    error "docker-compose / docker compose 均不可用，请安装后再继续。"
    all_ok=false
  fi

  # 检查必要文件
  local required_files=(
    "${SCRIPT_DIR}/docker-compose.yml.tpl"
    "${SCRIPT_DIR}/scripts/newest-images.list"
    "${SCRIPT_DIR}/configure.sh"
  )
  for f in "${required_files[@]}"; do
    if [[ -f "${f}" ]]; then
      success "文件存在：${f}"
    else
      warn "文件缺失：${f}"
    fi
  done

  if [[ "${all_ok}" == true ]]; then
    success "环境检查通过！"
  else
    die "环境检查发现问题，请修复后重试。"
  fi

  # 检查重要环境变量配置，如果为空，会导致较复杂的问题
  # 这些变量通常由 source ./configure.sh 注入
  if [[ -f "${SCRIPT_DIR}/configure.sh" ]]; then
    # shellcheck source=configure.sh
    source "${SCRIPT_DIR}/configure.sh"
  else
    warn "configure.sh 不存在，环境变量可能未设置。"
  fi

  _check_env() {
    local var="$1"
    if [[ -n "${!var:-}" ]]; then
      success "${var} 已设置：${!var}"
    else
      error "${var} 未设置，请在 configure.sh 中配置后重试。"
      all_ok=false
    fi
  }

  local env_vars=(
    "COSTRICT_BACKEND"
    "PORT_APISIX_ENTRY"
  )
  for v in "${env_vars[@]}"; do
    _check_env "${v}"
  done

  if [[ "${all_ok}" == false ]]; then
    die "存在必填环境变量未配置，请编辑 configure.sh 后重试。"
  fi

  bash ./docker-download-images.sh
  if [[ $? -ne 0 ]]; then
    die "镜像检查未通过"
  fi

  success "环境检查通过！"

}

# -----------------------------------------------------------------------------
# prepare — 准备部署环境（解析模板、生成配置）
# -----------------------------------------------------------------------------
cmd_prepare() {
  info "开始准备部署环境..."

  # 运行配置脚本，set -a 使所有变量自动 export 到子进程
  if [[ -f "${SCRIPT_DIR}/configure.sh" ]]; then
    # shellcheck source=configure.sh
    source "${SCRIPT_DIR}/configure.sh"
  else
    die "configure.sh 不存在，请在 configure.sh 中配置后重试。"
  fi

  # 解析模板
  if [[ -f "${SCRIPT_DIR}/scripts/template_gen.sh" ]]; then
    info "正在解析配置模板..."
    bash "${SCRIPT_DIR}/scripts/template_gen.sh"
    success "模板解析完成。"
  else
    die "scripts/template_gen.sh 不存在"
  fi

  bash "${SCRIPT_DIR}/scripts/prepare_dir.sh" "${SCRIPT_DIR}"
  success "部署环境准备完毕！"
}

# -----------------------------------------------------------------------------
# User Reminder — 用户提示
# -----------------------------------------------------------------------------

cmd_user_reminder() {
  info "管理用户访问 http://${COSTRICT_BACKEND}:${PORT_CASDOOR}/"
  info "配置Chat模型请访问 http://${COSTRICT_BACKEND}:${PORT_HIGRESS_CONTROL}/"
  info "BaseUrl请设置 http://${COSTRICT_BACKEND}:${PORT_APISIX_ENTRY}/"
}

# -----------------------------------------------------------------------------
# install — 完整安装（prepare + up）
# -----------------------------------------------------------------------------
cmd_install() {
  info "开始完整安装流程..."

  cmd_check
  cmd_prepare

  # 检查docker-compose.yml文件是否存在
  if [[ ! -f "${SCRIPT_DIR}/docker-compose.yml" ]]; then
    die "安装异常docker-compose.yml 不存在"
  fi
  info "开始安装..."
  docker compose up -d
  if [[ $? -ne 0 ]]; then
    die "安装异常"
  fi
  info "容器启动结束，准配配置路由"
  bash "${SCRIPT_DIR}/apisix_router_setting.sh"
  success "安装完成！"
  cmd_user_reminder
}

# -----------------------------------------------------------------------------
# down — 停止并移除所有容器
# -----------------------------------------------------------------------------
cmd_down() {
  info "正在停止所有服务..."

  local compose_file="${SCRIPT_DIR}/docker-compose.yml"
  if [[ ! -f "${compose_file}" ]]; then
    # 尝试模板文件
    compose_file="${SCRIPT_DIR}/docker-compose.yml.tpl"
    warn "docker-compose.yml 不存在，尝试使用 ${compose_file}"
  fi

  if docker compose -f "${compose_file}" down "$@" 2>/dev/null || \
     docker-compose -f "${compose_file}" down "$@" 2>/dev/null; then
    success "所有服务已停止并移除。"
  else
    die "停止服务失败，请检查 docker-compose 配置。"
  fi
}

# -----------------------------------------------------------------------------
# up — 启动所有服务
# -----------------------------------------------------------------------------
cmd_up() {
  info "正在启动所有服务..."

  local compose_file="${SCRIPT_DIR}/docker-compose.yml"
  if [[ ! -f "${compose_file}" ]]; then
    compose_file="${SCRIPT_DIR}/docker-compose.yml.tpl"
    warn "docker-compose.yml 不存在，尝试使用 ${compose_file}"
  fi

  if docker compose -f "${compose_file}" up -d "$@" 2>/dev/null || \
     docker-compose -f "${compose_file}" up -d "$@" 2>/dev/null; then
    success "所有服务已启动。"
    info "可通过 'docker compose ps' 查看容器状态。"
  else
    die "启动服务失败，请检查 docker-compose 配置或日志。"
  fi
}

# -----------------------------------------------------------------------------
# usage — 打印帮助信息
# -----------------------------------------------------------------------------
usage() {
  cat <<EOF
用法: $(basename "$0") <command> [options]

命令:
  check    检查运行环境（docker、docker-compose、docker 镜像、必要文件等）
  prepare  准备部署环境（解析模板、生成配置文件,创建文件夹等）或者 升级固定的配置文件
  install  完整安装（执行 check + prepare + 启动服务(up)）
  down     停止并移除所有容器（支持透传 docker-compose down 参数）
  up       启动所有服务（支持透传 docker-compose up 参数）

示例:
  $(basename "$0") check
  $(basename "$0") prepare
  $(basename "$0") install
  $(basename "$0") down --volumes
  $(basename "$0") up -d

EOF
}

# -----------------------------------------------------------------------------
# 初始化部署目录变量
# 优先使用环境变量 COSTRICT_DPLOY_DIR；若未设置则默认为本脚本所在目录
# -----------------------------------------------------------------------------
COSTRICT_DPLOY_DIR="${COSTRICT_DPLOY_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

# -----------------------------------------------------------------------------
# main — 入口函数
# -----------------------------------------------------------------------------
main() {
  if [[ $# -lt 1 ]]; then
    usage
    exit 1
  fi

  local command="$1"
  shift  # 移除第一个参数，剩余参数透传给子命令

  case "${command}" in
    check)
      cmd_check "$@"
      ;;
    prepare)
      cmd_prepare "$@"
      ;;
    install)
      cmd_install "$@"
      ;;
    down)
      cmd_down "$@"
      ;;
    up)
      cmd_up "$@"
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      error "未知命令：'${command}'"
      usage
      exit 1
      ;;
  esac
}

main "$@"
