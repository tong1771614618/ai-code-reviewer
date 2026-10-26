"""
简易日志模块 — 终端彩色输出 + 文件记录

为本项目精简版，保留核心日志方法：
- request / complete: 请求开始/结束
- llm / answer: LLM 调用
"""

import os
import re
import time
import logging
from datetime import datetime
from typing import Optional, Any


# ─── 日志文件 ───────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), 'storage', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'agent.log')
os.makedirs(LOG_DIR, exist_ok=True)

_file_logger = logging.getLogger('agent_file')
_file_logger.setLevel(logging.DEBUG)
_file_logger.propagate = False
if not _file_logger.handlers:
    fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
    fh.setFormatter(logging.Formatter('%(message)s'))
    _file_logger.addHandler(fh)


# ─── ANSI 颜色 ──────────────────────────────────────────────
class C:
    RESET = '\033[0m'; BOLD = '\033[1m'; DIM = '\033[2m'
    CYAN = '\033[36m'; GREEN = '\033[32m'; YELLOW = '\033[33m'
    RED = '\033[31m'; MAGENTA = '\033[35m'; BLUE = '\033[34m'
    WHITE = '\033[37m'; GRAY = '\033[90m'


def _strip_ansi(text: str) -> str:
    return re.sub(r'\033\[[0-9;]*m', '', text)


def _out(colored: str):
    print(colored, flush=True)
    _file_logger.info(_strip_ansi(colored))


def _preview(text: str, max_len: int = 60) -> str:
    text = str(text).replace('\n', ' ').strip()
    return text[:max_len] + '...' if len(text) > max_len else text


class AgentLogger:
    def __init__(self, project: str):
        self.project = project
        self._req_id = None
        self._start_time = 0.0
        self._total_tokens = 0

    def _gen_id(self) -> str:
        import hashlib
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:4]

    def _parse_usage(self, usage) -> tuple:
        in_tok = out_tok = total_tok = 0
        if usage:
            if hasattr(usage, 'prompt_tokens'):
                in_tok = usage.prompt_tokens or 0
                out_tok = usage.completion_tokens or 0
                total_tok = usage.total_tokens or 0
            elif isinstance(usage, dict):
                in_tok = usage.get('prompt_tokens', 0) or 0
                out_tok = usage.get('completion_tokens', 0) or 0
                total_tok = usage.get('total_tokens', 0) or 0
        self._total_tokens += total_tok
        return in_tok, out_tok, total_tok

    def request(self, message: str):
        self._req_id = self._gen_id()
        self._start_time = time.time()
        self._total_tokens = 0
        now = datetime.now().strftime('%H:%M:%S')
        _out(f'\n{C.DIM}━━━ {C.RESET}{C.CYAN}[{self.project}]{C.RESET} {C.BOLD}#{self._req_id}{C.RESET} '
             f'{C.WHITE}"{_preview(message, 40)}"{C.RESET}  {C.GRAY}{now}{C.RESET}{C.DIM} ━━━{C.RESET}')

    def llm(self, round: int = 1, model: str = '', temp: float = 0,
            usage: Any = None, decision: str = ''):
        in_tok, out_tok, total_tok = self._parse_usage(usage)
        parts = [f'{C.DIM}[R{round}]{C.RESET} {C.BOLD}LLM{C.RESET}']
        if model:
            parts.append(f'{C.GRAY}model={C.BLUE}{model}{C.RESET}')
        if temp:
            parts.append(f'{C.GRAY}temp={temp}{C.RESET}')
        _out('  '.join(parts))

    def answer(self, round: int, usage: Any = None, preview: str = ''):
        in_tok, out_tok, total_tok = self._parse_usage(usage)
        _out(f'{C.DIM}[R{round}]{C.RESET} {C.BOLD}LLM{C.RESET}')
        _out(f'     {C.GREEN}→ answer{C.RESET}')
        _out(f'     {C.GRAY}⏱ in={in_tok} out={out_tok} total={total_tok}{C.RESET}')
        if preview:
            _out(f'     预览: {C.WHITE}{_preview(preview, 50)}{C.RESET}')

    def complete(self, rounds: int = 1, tokens: int = 0, time_s: float = 0, agents: int = 0):
        elapsed = time_s or (time.time() - self._start_time)
        total = tokens or self._total_tokens
        parts = [f'{C.GREEN}✓{C.RESET} {rounds}轮']
        if agents:
            parts.append(f'{agents} agents')
        parts.append(f'{C.CYAN}{total}{C.RESET} tokens')
        parts.append(f'{C.YELLOW}{elapsed:.1f}s{C.RESET}')
        _out(f'{C.DIM}━━━ {" | ".join(parts)} ━━━━━━━━━━━━━━━━━━━{C.RESET}\n')


def agent_log(project: str) -> AgentLogger:
    return AgentLogger(project)
