import React from "react";
import axios from "axios";
import Cookies from "universal-cookie";
import TabSelector from "../components/TabSelector";

const cookies = new Cookies();
let url = "http://127.0.0.1:8000/api/";

class SendEmail extends React.Component {
  constructor() {
    super();
    this.state = {
      success: false,
      error: null,
      loading: false,
    };

    this.submit = this.submit.bind(this);

    if (cookies.get("token") === undefined) {
      window.location.href = "/auth";
    }
  }

  submit() {
    const { email, message } = this.state;

    this.setState({ loading: true, error: null }); // Начинаем загрузку

    axios({
      method: "POST",
      url: url + "send-email",
      headers: { Authorization: String(cookies.get("token")) },
      data: {
        email: email,
        message: message,
      },
    })
      .then((res) => {
        this.setState({
          success: true,
          loading: false, // Завершаем загрузку
        });
      })
      .catch((err) => {
        this.setState({
          error: "Ошибка при отправке письма. Пожалуйста, попробуйте еще раз.",
          loading: false, // Завершаем загрузку
        });
      });
  }

  render() {
    return (
      <>
        <TabSelector
          activeTab={"sendEmail"}
          onTabChange={this.handleTabChange}
          className="tab-selector"
        />
        <div>
          <p className="notification-text">
            РАССЫЛКА ОБРАЩЕНИЙ ИЗ ПОСЛЕДНЕГО ОБРАБОТАННОГО ФАЙЛА
          </p>
        </div>
        <button type="button" onClick={this.submit} className="button">
          Отправить
        </button>
        {this.state.loading && <p>Обработка...</p>}
        {this.state.success && (
          <p className="success-message">Письмо отправлено успешно!</p>
        )}
        {this.state.error && (
          <p className="error-message">{this.state.error}</p>
        )}
      </>
    );
  }
}

export { SendEmail };
