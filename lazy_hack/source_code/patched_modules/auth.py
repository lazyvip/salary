"""
假的授权模块 - 始终返回成功
"""

def ensure_license(*args, **kwargs):
    """确保授权 - 始终返回成功"""
    return "success"

def setup_periodic_license_check(*args, **kwargs):
    """设置定期检查 - 不执行任何操作"""
    pass

class LicenseChecker:
    """假的授权检查器"""
    
    def __init__(self):
        self.status = "success"
    
    def check(self, *args, **kwargs):
        return "success"
    
    def verify(self, *args, **kwargs):
        return True
    
    def validate(self, *args, **kwargs):
        return True

def ensure_license_with_loading(*args, **kwargs):
    """带加载的授权检查 - 始终成功"""
    return "success"

def ensure_license_with_progress(*args, **kwargs):
    """带进度的授权检查 - 始终成功"""
    return "success"
