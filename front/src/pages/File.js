import React from 'react';
import axios from 'axios';
import Cookies from 'universal-cookie';
import TabSelector from '../components/TabSelector';

const cookies = new Cookies();
let url = "http://127.0.0.1:8000/api/";

class File extends React.Component {
    constructor() {
        super();
        this.state = {
            selectedFile: '',
            weightType: 'light',
            dowm: false,
        };

        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleWeightChange = this.handleWeightChange.bind(this);
    }

    componentDidMount() {
        if (cookies.get('token') === undefined) {
            window.location.href = "/auth";
        }
    }

    handleInputChange(event) {
        this.setState({
            selectedFile: event.target.files[0]
        });
    }

    handleWeightChange(event) {
        this.setState({
            weightType: event.target.value
        });
    }

    submit() {
        const data = new FormData();
        data.append('file', this.state.selectedFile);
        data.append('weight_type', this.state.weightType);

        axios({
            method: 'POST',
            url: url + "upload-file",
            headers: { "Authorization": String(cookies.get('token')) },
            data: data
        })
        .then(res => {
            this.setState({
                dowm: true
            });
        });
    }

    dowl() {
        window.location.href = url + "upload-file";
    }

    render() {
        return (
            <div className="app-container">
                <TabSelector activeTab={"dataProcessing"} onTabChange={this.handleTabChange} className="tab-selector" />
                <h2 className="app-title">Загрузка файла</h2>
                
                <div className="form-wrapper">
                    <div className="form-group">
                        <label className="file-label">Выбрать файл:</label>
                        <input type="file" name="upload_file" onChange={this.handleInputChange} className="custom-input" />
                    </div>
                    <div className="form-group">
                        <label className="weight-label">Выбрать тип веса:</label>
                        <select value={this.state.weightType} onChange={this.handleWeightChange} className="custom-input">
                            <option value="light">Легкий</option>
                            <option value="medium">Средний</option>
                            <option value="heavy">Тяжелый</option>
                        </select>
                    </div>
                </div>

                <div className="spacer">
                    <button type='submit' onClick={() => this.submit()} className="button">Отправить</button>
                    {this.state.dowm && (
                        <button type='submit' onClick={() => this.dowl()} className="button">Скачать файл</button>
                    )}
                </div>
            </div>
        );
    }
}

export { File };