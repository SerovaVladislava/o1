import React from 'react';
import axios from 'axios';
import Cookies from 'universal-cookie';

const cookies = new Cookies();



class Auth extends React.Component{
    constructor(){
        super();
        this.state = {
            login: '',
            password: '',
        }

        this.handleInputLogin = this.handleInputLogin.bind(this);
        this.handleInputPassword = this.handleInputPassword.bind(this);
    }


    handleInputLogin(event) {
        this.setState({
            login: event.target.value
        })
    }
    handleInputPassword(event) {
        this.setState({
            password: event.target.value
        })
    }
    
            

    submit() {
        const login = this.state.login;
        const password = this.state.password;

        axios({
            method: 'POST',
            url: "http://127.0.0.1:8000/api/auth",
            data: {
                "login": login,
                "password": password
            }
        })
        .then(res => {
            const Newtoken = res.data.Authorization;
            cookies.set('token', Newtoken, 60);
            console.log(cookies.get('token'))
        window.location.href = "/";
            
        })


    }

    render() {
        return (
            <>
                <h1 style={{ textAlign: 'center', color: '#333' }}>Авторизация:</h1>
                <div style={{ maxWidth: '300px', margin: '0 auto', padding: '20px', border: '1px solid #ccc', borderRadius: '5px', boxSizing: 'border-box' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Логин:</label>
                    <input type="text" name="login" onChange={this.handleInputLogin} style={{ width: '100%', padding: '8px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc', boxSizing: 'border-box' }} /><br />
                    <label style={{ display: 'block', marginBottom: '5px' }}>Пароль:</label>
                    <input type="password" name="password" onChange={this.handleInputPassword} style={{ width: '100%', padding: '8px', marginBottom: '20px', borderRadius: '4px', border: '1px solid #ccc', boxSizing: 'border-box' }} />
                    <button type='submit' onClick={() => this.submit()} style={{ width: '100%', padding: '10px', backgroundColor: '#007BFF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', boxSizing: 'border-box' }}>Войти</button>
                </div>
                <p style={{ textAlign: 'center', marginTop: '20px', fontSize: '12px', color: 'gray' }}>
                    Если вы забыли почту или пароль, напишите администратору системы
                </p>
            </>
        );
    }
}

export {Auth};