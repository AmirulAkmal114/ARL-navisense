document.getElementById('btnLogin').addEventListener('click', function(event) {
    event.preventDefault();

    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    fetch(API_BASE + '/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, password: password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Login successful') {
            var userInfo = data.user_info[0];
            sessionStorage.setItem('firstname', userInfo.FirstName);
            sessionStorage.setItem('lastname', userInfo.LastName);
            sessionStorage.setItem('organization', userInfo.Organization);
            sessionStorage.setItem('email', userInfo.Email);
            sessionStorage.setItem('token', userInfo.Auth_Token);
            sessionStorage.setItem('timecreated', userInfo.Time_Created);
            sessionStorage.setItem('timeexpiry', userInfo.Time_Expiry);
            sessionStorage.setItem('package', userInfo.Package);
            window.location.href = 'map.html';
        } else {
            alert('Login failed. Please check your credentials.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});