document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.copy-button');
    buttons.forEach(function(button){
        const tooltipText = button.querySelector('.tooltip-text');
        button.addEventListener('click', function(event){
            const container = button.closest('.flex-container');
            const contentElement = container.querySelector('.readonly pre');
            const content = contentElement ? contentElement.textContent : '';
            copyTextToClipboard(content).then(function(){
                // 复制成功后，修改气泡框文字和样式
                tooltipText.textContent = '已复制';
                button.classList.add('copied');
            }).catch(function(err){
                console.error('无法复制文本: ', err);
            });
        });

        // 鼠标移出按钮后，恢复气泡框文字和样式
        button.addEventListener('mouseleave', function(){
            // 延迟恢复，确保点击后能看到“已复制”的提示
            setTimeout(function(){
                tooltipText.textContent = '复制';
                button.classList.remove('copied');
            }, 500);  // 您可以根据需要调整时间
        });
    });

    function copyTextToClipboard(text) {
        return new Promise(function(resolve, reject){
            if (!navigator.clipboard) {
                // 兼容性处理
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                try {
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    resolve();
                } catch (err) {
                    document.body.removeChild(textarea);
                    reject(err);
                }
                return;
            }
            navigator.clipboard.writeText(text).then(function() {
                resolve();
            }, function(err) {
                reject(err);
            });
        });
    }
});
