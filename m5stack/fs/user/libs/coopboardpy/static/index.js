const px1u = 60;
const pressedKeys = [];
var kb_lock = false;
function formatDate(date) {
    var year = date.getFullYear();
    var month = ("0" + (date.getMonth() + 1)).slice(-2); // Months are zero based, add leading 0 and slice last 2 digits
    var day = ("0" + date.getDate()).slice(-2); // Add leading 0 and slice last 2 digits
    var hours = ("0" + date.getHours()).slice(-2); // Add leading 0 and slice last 2 digits
    var minutes = ("0" + date.getMinutes()).slice(-2); // Add leading 0 and slice last 2 digits
    var seconds = ("0" + date.getSeconds()).slice(-2); // Add leading 0 and slice last 2 digits
    var milliseconds = ("00" + date.getMilliseconds()).slice(-3); // Add leading 00 and slice last 3 digits

    return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}.${milliseconds}`;
}

function on_off(type) {
    var btn = document.getElementsByClassName("btn-on")[0];
    var circle = document.getElementsByClassName("btn-on-circle")[0];
    var text = document.getElementsByClassName("btn-on-text")[0];
    kb_lock = type;

    if(!type){
      btn.style= "background-color: #ccc;"
      circle.style="left: 40px;background-color: #888;box-shadow: 0 0 10px #888;";
      text.style="right: 30px;color: #888;";
      text.innerText="OFF";
    } else {
      btn.style= ""
      circle.style="";
      text.style="";
      text.innerText="ON";
    }
    btn.setAttribute("onclick", "on_off(" + !type + ")"); // 修改状态
}

window.addEventListener('load', function() {
    // get hardware keyboard.
    fetch('/get_board')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // 遍历返回的二维数组，为每个数组元素（一行按键）创建一个新的div元素，并设置class为'row'
        data.forEach(key => {
          const keyboardContainer = document.getElementById('keyboard-container');
          const keyElement = document.createElement('div');
          keyElement.className = 'key';
          keyElement.id = key.gid;
          keyElement.textContent = key.name; // 设置按键上的文字
          keyElement.style.left = key.x * px1u + 'px';
          keyElement.style.top = key.y * px1u + 'px';
          keyElement.style.width = key.w * px1u + 'px'; // 设置按键的宽度
          keyElement.style.height = key.h * px1u + 'px'; // 你可以根据需要设置高度
          // 为所有class='key'的div设置鼠标按下抬起的键码事件
          keyElement.addEventListener('mousedown', function() {
            if (kb_lock) { // 锁住时
                const index = pressedKeys.indexOf(parseInt(this.id));
                if (index !== -1) { // 再次点击应该清除
                  pressedKeys.splice(index, 1);
                  this.style.color = '';
                } else {
                  pressedKeys.push(parseInt(this.id));
                  this.style.color = 'red';
                }
            } else {
              pressedKeys.push(parseInt(this.id));
            }
            sendPressedKeysToServer();
          });

          keyElement.addEventListener('mouseup', function() {
            if (!kb_lock) {
                // 从pressedKeys数组中移除当前键的ID
                const index = pressedKeys.indexOf(parseInt(this.id));
                if (index !== -1) {
                  pressedKeys.splice(index, 1);
                }
                sendPressedKeysToServer();
            }
          });
          keyboardContainer.appendChild(keyElement);
        });
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
      });

    const socket = io('ws://localhost:9999');  // 连接到服务器
    socket.on('connect', function() {
        console.log('Connected to the server');
    });
    socket.on('set_light', function(data) {
        rgbTuples =  data
        // 获取所有class='key'的div元素
        const keyDivs = document.getElementsByClassName('key');

        // 遍历每个div元素
        for (let i = 0; i < keyDivs.length; i++) {
            const div = keyDivs[i];

            // 检查我们是否还有足够的三元组来设置颜色
            if (i < rgbTuples.length) {
                const rgb = rgbTuples[i];

                // 设置div的背景颜色为RGB值
                div.style.backgroundColor = `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
            }
        }
    });

    socket.on('new_code', function(data) {
        let keyCodeDisplay = document.getElementById('keycode-container');
        // 如果子div数量达到5个，删除最旧的一个
        let childDivs = keyCodeDisplay.getElementsByClassName('keycode-item')
        if (childDivs.length >= 5) {
            keyCodeDisplay.removeChild(childDivs[0]);
        }
        // 创建新的子div元素
        let newDiv = document.createElement('div');
        newDiv.className = 'keycode-item';
        content = formatDate(new Date()) + '| ';
        if (data['ck']) {
            content += `<span class="composite-keycode">${data['ck']}</span>`;
        }
        content += ` <span class="keycode">${JSON.stringify(data['k_list'])}</span>`;
        newDiv.innerHTML = content;
        keyCodeDisplay.appendChild(newDiv);

    });

    function sendPressedKeysToServer() {
        socket.emit('set_key_down', pressedKeys)
    }

    on_off(kb_lock) // 初始化关闭按钮
});