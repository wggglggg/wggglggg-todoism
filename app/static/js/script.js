$(document).ready(function () {
    const ENTER_KEY = 13;
    const ESC_KEY = 27;

    $(document).ajaxError(function (event, request) {
        let message = null;

        if (request.responseJSON && request.responseJSON.hasOwnProperty('message')) {
            message = request.responseJSON.message;
        } else if (request.responseText) {
            let IS_JSON = true;
            try {
                var data = JSON.parse(request.responseText);
            }
            catch (err) {
                IS_JSON = false;
            }

            if (IS_JSON && data !== undefined && data.hasOwnProperty('message')) {
                message = JSON.parse(request.responseText).message;
            } else {
                message = default_error_message;
            }
        } else {
            message = default_error_message;
        }
        M.toast({html: message});
    });

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrf_token);
            }
        }
    });
    // Bind a callback that executes when document.location.hash changes.
    $(window).bind('hashchange', function () {
        // Some browers return the hash symbol, and some don't.
        let hash = window.location.hash.replace('#', '');
        let url;
        if (hash === 'login') {
            url = login_page_url
        } else if (hash === 'app') {
            url = app_page_url
        } else {
            url = intro_page_url
        }

        $.ajax({
            type: 'GET',
            url: url,
            success: function (data) {
                $('#main').hide().html(data).fadeIn(800);
                activeM();
            }
        });
    });

    if (window.location.hash === '') {
        window.location.hash = '#intro'; // home page, show the default view
    } else {
        $(window).trigger('hashchange'); // user refreshed the browser, fire the appropriate function
    }

    function toggle_password() {
        let password_input = document.getElementById('password-input');
        if (password_input.type === 'password') {
            password_input.type = 'text';
        } else {
            password_input.type = 'password';
        }
    }

    $(document).on('click', '#toggle-password', toggle_password);

    function display_dashboard() {
        let all_count = $('.item').length;
        if (all_count === 0) {
            $('#dashboard').hide();
        } else {
            $('#dashboard').show();
            $('ul.tabs').tabs();
        }
    }

    function activeM() {
        $('.sidenav').sidenav();
        $('ul.tabs').tabs();
        $('.modal').modal();
        $('.tooltipped').tooltip();
        $('.dropdown-trigger').dropdown({
                constrainWidth: false,
                coverTrigger: false
            }
        );
        display_dashboard();
    }


    function register() {
        $.ajax({
            type: 'GET',
            url: register_url,
            success: function (data) {
                $('#username-input').val(data.username);
                $('#password-input').val(data.password);
                M.toast({html: data.message})
            }
        });
    }

    $(document).on('click', '#register-btn', register);

    function login_user() {
        let username = $('#username-input').val();
        let password = $('#password-input').val();
        if (!username || !password) {
            M.toast({html: login_error_message});
            return;
        }

        let data = {
            'username': username,
            'password': password
        };
        $.ajax({
            type: 'POST',
            url: login_url,
            data: JSON.stringify(data),
            contentType: 'application/json;charset=UTF-8',
            success: function (data) {
                if (window.location.hash === '#app' || window.location.hash === 'app') {
                    $(window).trigger('hashchange');
                } else {
                    window.location.hash = '#app';
                }
                activeM();
                M.toast({html: data.message});
            }
        });
    }

    $(document).on('click', '#login-btn', login_user);
    
    
    function logout_user() {
        $.ajax({
            type: 'GET',
            url: logout_url,
            success: function (data) {
                window.location.hash = '#intro';
                activeM();
                M.toast({html: data.message})
            }
        });
    }

    $(document).on('click', '#logout-btn', logout_user);

    // 刷新计数
    function refresh_count () {                  // 刷新 Item计数
        let $items = $('.item');                   // 获取所有的item

        display_dashboard();                        // 刷新 一下面板, 如果没有了Item要隐藏面板
        let all_count = $items.length;
        console.log('all_count', all_count)
        let active_count = $items.filter(function () {   // 滤过还未完成的事项
            return $(this).data('done') === false;
        }).length;
        let completed_count = $items.filter(function () {
            return $(this).data('done') === true;
        }).length;
        $('#all_count').html(all_count);                       // 修改页面id = 'all_count'
        $('#active_count').html(active_count);
        $('#active-count-nav').html(active_count);
        $('#completed_count').html(completed_count);
    }


    function new_item(e) {
        let $input = $('#item-input');
        let value = $input.val().trim();
        if (e.which !== ENTER_KEY || !value) {
            return;                                 // 如果回车键没有按下, 或者新建待办事件为空
        }
        $input.focus().val('');                      // 监听新添加待办事项输入框, 清空输入框
        $.ajax({
            type: 'POST',
            url: new_item_url,
            data: JSON.stringify({'body': value}),      // 输入的值 生成Json字符串
            contentType: 'application/json;charset=UTF-8',      // 支持中文
            success: function (data) {
                M.toast({html: data.message, classes: 'rounded'}); // 显示消息, 主题rounded
                $('.items').append(data.html);                          // 将新待办插入到class='items'中
                activeM();
                refresh_count();
            }
        });
    }


    function remove_edit_input() {          // 取消修改或者删除 事项
        let $edit_input = $('#edit-item-input');    // 获取修改元素
        let $input = $('#item-input');

        $edit_input.parent().prev().show();          // 将前一面被 隐藏过的Item显示出来
        $edit_input.parent().remove();
        $input.focus();                             // 修改完事项后， 光标移到新建待办事项上
    }


    $(document).on('keyup', '#item-input', new_item.bind(this));

    $(document).on('mouseenter', '.item', function () {   //  鼠标移入class='item'元素时, 去除hide, 从而显示icon
        $(this).find('.edit-btns').removeClass('hide');
    })
        .on('mouseleave', '.item', function () {
        $(this).find('.edit-btns').addClass('hide')
    });


    function edit_btn() {
        let $item = $(this).parent().parent();              //  获取当前.edit_btn元素的父元素=>父元素div

        let itemId = $item.data('id');                      //  div 里面的data-id
        console.log('itemId:  ',itemId);
        let itemBody = $('#body' + itemId).text().trim();          // 获取此id = "bodyid" 的 text信息,{{item.body}}
        console.log('$itemBody264:', itemBody);
        $item.hide();                                       // 隐藏此div
        //  在隐藏的div元素后面插入一个div， 里面为input输入框，  value值与隐藏的value一值
        $item.after('\
                <div class="row card-panel hoverable">\
                <input class="validate" id="edit-item-input" type="text" value="' + itemBody + '"\
                autocomplete="off" autofocus required> \
                </div> \
                ');

        let $edit_input = $('#edit-item-input');                     // 获取刚插入的元素
        let strLength = $edit_input.val().length * 2;                // 确保光标在最后一个字后面
        $edit_input.focus();                                        // 绑定#edit-item-input, 也叫 聚集在这个id
        $edit_input[0].setSelectionRange(strLength, strLength);     // 控制光标的位置

        $(document).on('keydown', function (e) {                    // 判断按键是否为esc, 这样就取消修改操作
            if (e.keyCode === ESC_KEY) {
                remove_edit_input();
            }
        });

        $edit_input.on('focusout', function () {
            remove_edit_input();
        });
    }

    $(document).on('click', '.edit-btn', edit_btn);

    // 编辑item
    function edit_item(e) {
        let $edit_input = $('#edit-item-input');
        let value = $edit_input.val().trim();                   // 去除#edit-item-input值   前后的空格
        if (e.which !== ENTER_KEY || !value) {                  // 如果编辑完不是回车,或者数据无效, 就不做任何反应
            return;
        }
        $edit_input.val('');                                     // 如果是回车, 填充为空字符串

        if (!value) {                                            // 如果是空信息, 提示
            M.toast({html: empty_body_error_message})
        }

        let url = $edit_input.parent().prev().data('href');           // 被 隐藏的同id 元素, 获取它的href作为url
        let id = $edit_input.parent().prev().data('id');

        $.ajax({
            type: 'PUT',
            url: url,
            data: JSON.stringify({'body': value}),
            contentType: 'application/json;charset=UTF-8',
            success: function (data) {
                $('#body' + id).html(value);
                $edit_input.parent().prev().data('body', value);
                remove_edit_input();
                M.toast({html: data.message});
            }
        });
    }

    $(document).on('keyup', '#edit-item-input', edit_item.bind(this));

    // 删除待办事项
    function delete_item() {
        let $input = $('#item-input');                  // 删除时光标停留在 新建事项栏  铺垫
        let $item = $(this).parent().parent();          // 点击删除的待办事项的父父元素, 也就是点击的当前待办事项

        $input.focus();
        $.ajax({
            type: 'DELETE',
            url: $(this).data('href'),                  // 获取 删除待办事项的  data-href里面的地址
            success: function (data) {
                $item.remove();                         // 从页面上移除此条待办事项
                activeM();                              // 再次激活materialize插件
                refresh_count();                        // 将数量重新刷新
                M.toast({html: data.message});          // 从后台拿到data, 将里面的massage属性信息显示到页面
            }
        });
    }

    $(document).on('click', '.delete-btn', delete_item);


    // 切换事项 完成 与 未完成 状态
    function toggle_item() {
    let $input = $('#item-input');
    $input.focus();

    let $item = $(this).parent().parent();
    let $this = $(this);

    if ($item.data('done')) {               // 如果当前状态是 已多选(已完成)
        $.ajax({
            type: 'PATCH',
            url: $this.data('href'),
            success: function (data) {      // 如果是已完成, 就将inactive 改为active, 这样字是可以改的
                $this.next().removeClass('inactive-item');
                $this.next().addClass('active-item');
                $this.find('i').text('check_box_outline_blank');
                $item.data('done', false);      //  class='item'的 data-done  改为false也就是未完成
                M.toast({html: data.message});
                refresh_count();
            },
        });
    } else {                                // 如果是未完成, 就将active 改为inactive, 事项就灰色了
        $.ajax({
            type: 'PATCH',
            url: $this.data('href'),
            success: function (data) {
                $this.next().removeClass('active-item');
                $this.next().addClass('inactive-item');
                $this.find('i').text('check_box');
                $item.data('done', true);
                M.toast({html: data.message});
                refresh_count();
            },
        });
    }
    }

    $(document).on('click', '.done-btn', toggle_item);
    
    // 一键删除已完成的待办事项
    function clear_all() {
        let $input = $('#item-input');
        let $items = $('.item');

        $input.focus();

        $.ajax({
            type: 'DELETE',
            url: clear_item_url,
            success: function (data) {
                $items.filter(function () {
                    return $(this).data('done');
                }).remove();
                M.toast({html: data.message, classes: 'rounded'});
                refresh_count();
            }
        });
    }

    $(document).on('click', '#clear-btn', clear_all);

    // 只显示 未完成 事项
    function display_active_items() {
        let $input = $('#item-input');
        let $items = $('.item');

        $input.focus();
        $items.show();
        $items.filter(function () {
            return $(this).data('done');
        }).hide();
    }

    $(document).on('click', '#active-item', display_active_items);

    // 只显示 已完成 事项
    function display_completed_items() {
        let $input = $('item-input');
        let $items = $('.item');

        $input.focus();
        $items.show();
        $items.filter(function () {
            return !$(this).data('done');        // 返回return已完成的事项 将被隐藏起来
        }).hide();
    }

    $(document).on('click', '#completed-item', display_completed_items);

    // 显示所有的待办事项  (已完成 + 未完成)
    function display_all_items() {
        let $input = $('item-input');
        let $items = $('.item');

        $input.focus();
        $items.show();
    }

    $(document).on('click', '#all-item', display_all_items);

    // 切换语言
    function lang_btn() {
        $.ajax({
            type: 'GET',
            url: $(this).data('href'),
            success: function (data) {
                $(window).trigger('hashchange');
                activeM();
                M.toast({html: data.message});
            }
        });
    }

    $(document).on('click', '.lang-btn',lang_btn);

    // 切换时区
    function timezone_btn() {
        $.ajax({
            type: 'GET',
            url: $(this).data('href'),
            success: function (data) {
                activeM();
                M.toast({html: data.message})
            }
        });
    }

    $(document).on('click', '.timezone-btn', timezone_btn);

    activeM();  // initialize Materialize
});
