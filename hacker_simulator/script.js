document.addEventListener('DOMContentLoaded', function() {
    // 元素引用
    const startBtn = document.getElementById('start-btn');
    const warning = document.querySelector('.warning');
    const hackerScreen = document.getElementById('hacker-screen');
    const output = document.getElementById('output');
    const input = document.getElementById('input');
    const cursor = document.getElementById('cursor');
    const status = document.getElementById('status');
    const progress = document.getElementById('progress');
    const statusText = document.getElementById('status-text');
    const panel1 = document.getElementById('panel1');
    const panel2 = document.getElementById('panel2');
    
    // 预设的"黑客"文本
    const hackerTexts = [
        "正在访问主服务器...",
        "绕过防火墙...",
        "注入SQL查询...",
        "破解密码哈希...",
        "获取管理员权限...",
        "下载敏感数据...",
        "清除访问日志...",
        "部署后门程序...",
        "建立远程连接...",
        "加密通信通道...",
        "扫描网络漏洞...",
        "执行跨站脚本...",
        "拦截网络流量...",
        "破解加密算法...",
        "访问隐藏API...",
        "绕过双因素认证...",
        "修改系统配置...",
        "植入木马程序...",
        "执行DDoS攻击...",
        "篡改数据库记录..."
    ];
    
    // 随机代码片段
    const codeSnippets = [
        "for(i=0;i<len;i++){data[i]=decrypt(buffer[i]);}",
        "if(access.level < 4){return 'ACCESS DENIED';}",
        "while(socket.isConnected()){stream.readBytes(buffer);}",
        "try{exec(cmd);}catch(e){log.error('Failed: '+e);}",
        "function bypass(fw){return fw.findVulnerability();}",
        "class Exploit{constructor(){this.payload=payload;}}",
        "const encrypted = cipher.update(text, 'utf8', 'hex');",
        "let keys = await crypto.subtle.generateKey(algo, true, ['encrypt']);",
        "ssh.connect({host:target,port:22,user:'root',pass:cracked});",
        "SELECT * FROM users WHERE username='' OR '1'='1';",
        "document.cookie.split(';').forEach(c => {tokens.push(c.trim())});",
        "curl -X POST https://api.target.com/login -d 'user=admin&pass='+pass;",
        "sudo chmod -R 777 /var/www/html",
        "grep -r \"password\" /home/ --include=\"*.txt\"",
        "nmap -sS -sV -O -p- 192.168.1.1/24"
    ];
    
    // 随机IP地址生成
    function generateRandomIP() {
        return `${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}`;
    }
    
    // 随机端口生成
    function generateRandomPort() {
        return Math.floor(Math.random() * 65535) + 1;
    }
    
    // 随机十六进制地址生成
    function generateRandomHex(length) {
        let result = '0x';
        const characters = '0123456789ABCDEF';
        for (let i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        return result;
    }
    
    // 添加扫描线效果
    function addScanLine() {
        const scanLine = document.createElement('div');
        scanLine.className = 'scan-line';
        document.querySelector('.main-screen').appendChild(scanLine);
    }
    
    // 添加文本到输出区域
    function addOutput(text, delay = 50) {
        return new Promise(resolve => {
            let index = 0;
            const element = document.createElement('div');
            element.className = 'text-appear';
            output.appendChild(element);
            
            const interval = setInterval(() => {
                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;
                    // 自动滚动到底部
                    output.scrollTop = output.scrollHeight;
                } else {
                    clearInterval(interval);
                    resolve();
                }
            }, delay);
        });
    }
    
    // 模拟输入
    function simulateTyping(text, delay = 100) {
        return new Promise(resolve => {
            let index = 0;
            input.textContent = '';
            
            const interval = setInterval(() => {
                if (index < text.length) {
                    input.textContent += text.charAt(index);
                    index++;
                } else {
                    clearInterval(interval);
                    setTimeout(resolve, 500);
                }
            }, delay);
        });
    }
    
    // 更新进度条
    function updateProgress(percent) {
        progress.style.width = `${percent}%`;
    }
    
    // 更新状态文本
    function updateStatus(text) {
        status.textContent = text;
    }
    
    // 更新底部状态文本
    function updateStatusText(text) {
        statusText.textContent = text;
    }
    
    // 填充侧面板
    function fillPanel(panel) {
        let content = '';
        for (let i = 0; i < 15; i++) {
            const type = Math.floor(Math.random() * 3);
            if (type === 0) {
                content += `${generateRandomIP()}:${generateRandomPort()}<br>`;
            } else if (type === 1) {
                content += `${generateRandomHex(8)}: ${Math.floor(Math.random() * 100)}%<br>`;
            } else {
                content += `${codeSnippets[Math.floor(Math.random() * codeSnippets.length)]}<br>`;
            }
        }
        panel.innerHTML = content;
    }
    
    // 创建弹窗
    function createPopup(text, duration = 3000) {
        const popup = document.createElement('div');
        popup.className = 'popup';
        popup.textContent = text;
        popup.style.top = `${Math.random() * 70 + 10}%`;
        popup.style.left = `${Math.random() * 70 + 10}%`;
        popup.style.width = `${Math.random() * 200 + 150}px`;
        document.body.appendChild(popup);
        
        setTimeout(() => {
            popup.remove();
        }, duration);
    }
    
    // 主要的"黑客"模拟序列
    async function runHackingSimulation() {
        addScanLine();
        updateStatus("活跃");
        
        // 初始化侧面板
        fillPanel(panel1);
        fillPanel(panel2);
        
        // 欢迎消息
        await addOutput("终端已激活. 正在初始化系统...");
        await addOutput("系统已就绪. 输入命令开始操作.");
        
        // 模拟用户输入
        await simulateTyping("run hack.exe --target=192.168.1.1 --mode=stealth");
        input.textContent = '';
        await addOutput("> run hack.exe --target=192.168.1.1 --mode=stealth");
        await addOutput("正在启动黑客工具...");
        
        // 模拟黑客进度
        let progressValue = 0;
        const progressInterval = setInterval(() => {
            progressValue += Math.random() * 5;
            if (progressValue > 100) progressValue = 100;
            updateProgress(progressValue);
            
            if (progressValue >= 100) {
                clearInterval(progressInterval);
            }
        }, 1000);
        
        // 随机显示黑客文本
        for (let i = 0; i < 15; i++) {
            const randomText = hackerTexts[Math.floor(Math.random() * hackerTexts.length)];
            await addOutput(randomText);
            updateStatusText(randomText);
            
            // 随机更新侧面板
            if (Math.random() > 0.5) fillPanel(panel1);
            if (Math.random() > 0.5) fillPanel(panel2);
            
            // 随机弹窗
            if (Math.random() > 0.7) {
                createPopup(`警告: ${hackerTexts[Math.floor(Math.random() * hackerTexts.length)]}`);
            }
            
            // 随机代码片段
            if (Math.random() > 0.6) {
                const code = codeSnippets[Math.floor(Math.random() * codeSnippets.length)];
                await addOutput(`执行代码: ${code}`, 10);
            }
            
            // 随机IP和端口信息
            if (Math.random() > 0.6) {
                await addOutput(`连接到: ${generateRandomIP()}:${generateRandomPort()}`);
            }
            
            // 随机等待
            await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
        }
        
        // 完成黑客模拟
        updateProgress(100);
        updateStatus("完成");
        updateStatusText("黑客模拟完成");
        await addOutput("操作完成. 目标已被成功入侵.");
        await addOutput("按任意键继续...");
    }
    
    // 键盘事件监听
    document.addEventListener('keydown', function(event) {
        if (warning.style.display === 'none') {
            // 如果已经开始模拟，任何按键都会触发新的模拟
            output.innerHTML = '';
            input.textContent = '';
            updateProgress(0);
            runHackingSimulation();
        }
    });
    
    // 点击开始按钮
    startBtn.addEventListener('click', function() {
        warning.style.display = 'none';
        hackerScreen.style.display = 'flex';
        document.querySelector('.home-link').style.display = 'block';
        runHackingSimulation();
    });
});