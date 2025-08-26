document.addEventListener('DOMContentLoaded', function() {
    const particlesContainer = document.getElementById('particles');
    
    // 创建粒子
    for(let i = 0; i < 100; i++) {
        createParticle();
    }
    
    function createParticle() {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = '2px';
        particle.style.height = '2px';
        particle.style.background = `rgba(${Math.random() * 255}, ${Math.random() * 255}, 255, 0.7)`;
        particle.style.borderRadius = '50%';
        particle.style.left = Math.random() * 100 + 'vw';
        particle.style.top = Math.random() * 100 + 'vh';
        particle.style.pointerEvents = 'none';
        
        particlesContainer.appendChild(particle);
        
        animateParticle(particle);
    }
    
    function animateParticle(particle) {
        const duration = 3000 + Math.random() * 5000;
        const keyframes = [
            { transform: 'translate(0, 0)', opacity: 0 },
            { transform: `translate(${Math.random() * 200 - 100}px, ${Math.random() * 200 - 100}px)`, opacity: 1 },
            { transform: `translate(${Math.random() * 200 - 100}px, ${Math.random() * 200 - 100}px)`, opacity: 0 }
        ];
        
        const animation = particle.animate(keyframes, {
            duration: duration,
            iterations: Infinity
        });
        
        animation.onfinish = () => {
            particle.remove();
            createParticle();
        };
    }
    
    // 为每个卡片添加鼠标跟随效果
    document.querySelectorAll('.card-wrap').forEach(cardWrap => {
        const card = cardWrap.querySelector('.card');
        const cardBg = cardWrap.querySelector('.card-bg');
        let width = cardWrap.offsetWidth;
        let height = cardWrap.offsetHeight;
        let mouseX = 0;
        let mouseY = 0;
        let mouseLeaveDelay = null;
        
        // 更新尺寸
        function updateSize() {
            width = cardWrap.offsetWidth;
            height = cardWrap.offsetHeight;
        }
        
        cardWrap.addEventListener('mouseenter', function() {
            clearTimeout(mouseLeaveDelay);
            updateSize();
        });
        
        cardWrap.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            mouseX = e.clientX - rect.left - width / 2;
            mouseY = e.clientY - rect.top - height / 2;
            
            const mousePX = mouseX / width;
            const mousePY = mouseY / height;
            
            // 卡片3D旋转
            const rX = mousePX * 30;
            const rY = mousePY * -30;
            card.style.transform = `rotateY(${rX}deg) rotateX(${rY}deg)`;
            
            // 背景视差移动
            const tX = mousePX * -40;
            const tY = mousePY * -40;
            if (cardBg) {
                cardBg.style.transform = `translateX(${tX}px) translateY(${tY}px)`;
            }
        });
        
        cardWrap.addEventListener('mouseleave', function() {
            mouseLeaveDelay = setTimeout(() => {
                card.style.transform = 'rotateY(0deg) rotateX(0deg)';
                if (cardBg) {
                    cardBg.style.transform = 'translateX(0px) translateY(0px)';
                }
            }, 1000);
        });
    });
});