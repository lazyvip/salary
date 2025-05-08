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
    
    // 添加鼠标移动效果
    document.addEventListener('mousemove', function(e) {
        const cards = document.querySelectorAll('.card');
        const mouseX = e.clientX;
        const mouseY = e.clientY;
        
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const cardX = rect.left + rect.width / 2;
            const cardY = rect.top + rect.height / 2;
            
            const angleX = (mouseY - cardY) / 30;
            const angleY = (mouseX - cardX) / -30;
            
            card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) translateY(-10px)`;
        });
    });
    
    // 重置卡片位置
    document.addEventListener('mouseleave', function() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });
});