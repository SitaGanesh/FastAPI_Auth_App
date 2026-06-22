const API= "http://localhost:8000"

const GOOGLE_CLIENT_ID="993187631083-5v4jrd3nib7cqt216a87hssoe821igd9.apps.googleusercontent.com";
const GOOGLE_REDIRECT_URL="http://localhost:5500/frontend/login.html";

async function register(){
    const data={
        username: document.getElementById("username").value,
        email:document.getElementById("email").value,
        password:document.getElementById("password").value
    };
    await fetch(`${API}/register`,{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify(data)
    })
    alert("Registered")
}

async function login(){
    const data = {
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value
    };

    const response = await fetch(`${API}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    // Check if the HTTP response status is 200-299
    if (response.ok && result.success) {
        localStorage.setItem("username", result.username);
        window.location.href = "welcome.html";
    } else {
        // If it's a 400 error, FastAPI places our string inside result.detail
        const errorMessage = result.detail || "Invalid credentials";
        alert(errorMessage);
    }
}


function redirectToGoogle(){
    const googleAuthUrl=`https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(GOOGLE_REDIRECT_URL)}&response_type=code&scope=${encodeURIComponent("openid email profile")}&access_type=offline&prompt=consent`;
    window.location.href=googleAuthUrl;
}
window.onload=async function(){
    const urlParams=new URLSearchParams(window.location.search);
    const code=urlParams.get('code');
    if(code){
        window.history.replaceState({},document.title,window.location.pathname);
        try{
            const response=await fetch(`${API}/auth/google`,{
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body: JSON.stringify({code:code})
            });
            const result=await response.json();
            if(response.ok && result.success){
                localStorage.setItem("username",result.username);
                window.location.href="welcome.html";
            }else{
                alert(result.detail || "Google authentication failed");
            }
        }
        catch(error){
            console.error("Error during Google authentication:",error);
            alert("An error occurred during Google authentication")
        }
    }
}