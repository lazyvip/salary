document.addEventListener('DOMContentLoaded', function() {
    // 获取页面元素
    const inputPage = document.getElementById('input-page');
    const timerPage = document.getElementById('timer-page');
    const startWorkBtn = document.getElementById('start-work');
    const endWorkBtn = document.getElementById('end-work');
    const timerElement = document.getElementById('timer');
    const earnedAmountElement = document.getElementById('earned-amount');
    const moneyRainElement = document.getElementById('money-rain');
    
    // 输入字段
    const monthlySalaryInput = document.getElementById('monthly-salary');
    const hoursPerDayInput = document.getElementById('hours-per-day');
    const daysPerMonthInput = document.getElementById('days-per-month');
    
    // 计时器变量
    let startTime;
    let timerInterval;
    let hourlyRate;
    let moneyRainInterval;
    
    // 格式化数字为两位数
    function formatNumber(num) {
        return num.toString().padStart(2, '0');
    }
    
    // 更新计时器显示
    function updateTimer() {
        const currentTime = new Date();
        const elapsedTime = new Date(currentTime - startTime);
        const days = Math.floor(elapsedTime / (24 * 60 * 60 * 1000));
        const hours = elapsedTime.getUTCHours();
        const minutes = elapsedTime.getUTCMinutes();
        const seconds = elapsedTime.getUTCSeconds();
        
        timerElement.textContent = `${formatNumber(days)}:${formatNumber(hours)}:${formatNumber(minutes)}:${formatNumber(seconds)}`;
        
        // 计算已赚金额
        const elapsedHours = days * 24 + hours + minutes / 60 + seconds / 3600;
        const earned = elapsedHours * hourlyRate;
        earnedAmountElement.textContent = `￥${earned.toFixed(2)}`;
    }
    
    // 创建金钱元素
    function createMoneyElement() {
        const money = document.createElement('div');
        money.className = 'money';
        
        // 随机位置
        const startPositionX = Math.random() * window.innerWidth;
        money.style.left = `${startPositionX}px`;
        
        // 随机大小 (30px - 50px)
        const size = Math.random() * 20 + 30;
        money.style.width = `${size}px`;
        money.style.height = `${size}px`;
        
        // 随机旋转
        const rotation = Math.random() * 360;
        money.style.transform = `rotate(${rotation}deg)`;
        
        // 随机下落速度 (3-8秒)
        const fallDuration = Math.random() * 5 + 3;
        money.style.animationDuration = `${fallDuration}s`;
        
        // 添加到容器
        moneyRainElement.appendChild(money);
        
        // 动画结束后移除
        setTimeout(() => {
            money.remove();
        }, fallDuration * 1000);
    }
    
    // 开始金钱雨
    function startMoneyRain() {
        moneyRainElement.style.display = 'block';
        // 每200-500ms创建一个新的金钱元素
        moneyRainInterval = setInterval(() => {
            createMoneyElement();
        }, Math.random() * 300 + 200);
    }
    
    // 停止金钱雨
    function stopMoneyRain() {
        clearInterval(moneyRainInterval);
        moneyRainElement.style.display = 'none';
        // 清除所有金钱元素
        moneyRainElement.innerHTML = '';
    }
    
    // 开始上班
    startWorkBtn.addEventListener('click', function() {
        // 验证输入
        const monthlySalary = parseFloat(monthlySalaryInput.value);
        const hoursPerDay = parseFloat(hoursPerDayInput.value);
        const daysPerMonth = parseFloat(daysPerMonthInput.value);
        
        if (!monthlySalary || !hoursPerDay || !daysPerMonth) {
            alert('请填写所有必填字段！');
            return;
        }
        
        if (monthlySalary <= 0 || hoursPerDay <= 0 || daysPerMonth <= 0) {
            alert('所有输入值必须大于0！');
            return;
        }
        
        // 计算时薪
        hourlyRate = monthlySalary / (hoursPerDay * daysPerMonth);
        
        // 切换到计时页面
        inputPage.classList.remove('active');
        timerPage.classList.add('active');
        
        // 开始计时
        startTime = new Date();
        updateTimer();
        timerInterval = setInterval(updateTimer, 1000);
        
        // 开始金钱雨动画
        startMoneyRain();
    });
    
    // 结束上班
    endWorkBtn.addEventListener('click', function() {
        // 停止计时器
        clearInterval(timerInterval);
        
        // 停止金钱雨
        stopMoneyRain();
        
        // 切换回输入页面
        timerPage.classList.remove('active');
        inputPage.classList.add('active');
        
        // 重置计时器显示
        timerElement.textContent = '00:00:00:00';
        earnedAmountElement.textContent = '￥0.00';
    });
});