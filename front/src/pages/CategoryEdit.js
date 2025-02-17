import React from "react";
import axios from "axios";
import Cookies from "universal-cookie";
import TabSelector from "../components/TabSelector";

const cookies = new Cookies();
let url = "http://127.0.0.1:8000/api/";

class CategoryEdit extends React.Component {
  constructor() {
    super();
    this.state = {
      categories: {},
      keywords: [],
      newCategory: "",
      newCategoryEmail: "",
      newKeyword: "",
      selectedCategory: "",
      activeTab: "categories", // Default active tab
      searchKeyword: "",
    };
    this.handleCategoryChange = this.handleCategoryChange.bind(this);
    this.handleCategoryEmailChange = this.handleCategoryEmailChange.bind(this);
    this.handleKeywordChange = this.handleKeywordChange.bind(this);
    this.addCategory = this.addCategory.bind(this);
    this.addKeyword = this.addKeyword.bind(this);
    this.removeCategory = this.removeCategory.bind(this);
    this.removeKeyword = this.removeKeyword.bind(this);
    this.saveChanges = this.saveChanges.bind(this);
    this.setActiveTab = this.setActiveTab.bind(this);
    this.handleSearchChange = this.handleSearchChange.bind(this);
  }

  componentDidMount() {
    this.fetchCategories();
    this.fetchKeywords();
  }

  fetchCategories() {
    axios
      .get(url + "categories", {
        headers: { Authorization: String(cookies.get("token")) },
      })
      .then((res) => {
        const categories = res.data.categories.reduce((acc, category) => {
          acc[category] = [];
          return acc;
        }, {});
        this.setState({ categories });
      });
  }

  fetchKeywords() {
    axios
      .get(url + "keywords", {
        headers: { Authorization: String(cookies.get("token")) },
      })
      .then((res) => {
        this.setState({ keywords: res.data.keywords });
      });
  }

  handleCategoryChange(event) {
    this.setState({ newCategory: event.target.value });
  }

  handleCategoryEmailChange(event) {
    this.setState({ newCategoryEmail: event.target.value });
  }

  handleKeywordChange(event) {
    this.setState({ newKeyword: event.target.value });
  }

  addCategory() {
    const { newCategory, newCategoryEmail } = this.state;
    if (newCategory && newCategoryEmail) {
      // Добавление новой категории с почтой
      axios
        .post(
          url + "categories/",
          {
            category_name: newCategory,
            email: newCategoryEmail,
          },
          {
            headers: { Authorization: String(cookies.get("token")) },
          }
        )
        .then(() => {
          this.setState((prevState) => ({
            categories: { ...prevState.categories, [newCategory]: [] },
            newCategory: "",
            newCategoryEmail: "",
          }));
        })
        .catch((error) => {
          console.error("Error adding category:", error);
        });
    }
  }

  addKeyword() {
    const { newKeyword, keywords } = this.state;
    if (newKeyword && !keywords.includes(newKeyword)) {
      this.setState((prevState) => ({
        keywords: [...prevState.keywords, newKeyword],
        newKeyword: "",
      }));
    }
  }

  removeCategory(category) {
    const { categories } = this.state;
    const newCategories = { ...categories };
    delete newCategories[category];
    this.setState({ categories: newCategories });

    // Удаление категории через новый CategoryUpdateView с флагом
    axios
      .post(
        url + "categories/",
        {
          category_name: category,
          delete: true, // Установка флага для удаления
        },
        {
          headers: { Authorization: String(cookies.get("token")) },
        }
      )
      .then(() => {
        console.log(`Category "${category}" deleted successfully.`);
      })
      .catch((error) => {
        console.error("Error deleting category:", error);
      });
  }

  removeKeyword(keyword) {
    const { keywords } = this.state;
    const newKeywords = keywords.filter((kw) => kw !== keyword);
    this.setState({ keywords: newKeywords });
  }

  saveChanges() {
    const { keywords } = this.state;
    axios
      .post(
        url + "keywords",
        {
          keywords,
        },
        {
          headers: { Authorization: String(cookies.get("token")) },
        }
      )

      .then(() => {
        alert("Changes saved successfully!");
      });
  }

  setActiveTab(tab) {
    this.setState({ activeTab: tab });
  }

  handleSearchChange(event) {
    this.setState({ searchKeyword: event.target.value });
  }

  render() {
    const {
      categories,
      keywords,
      newCategory,
      newCategoryEmail,
      newKeyword,
      activeTab,
      searchKeyword,
    } = this.state;
    const filteredKeywords = keywords.filter((keyword) =>
      keyword.includes(searchKeyword)
    );
    return (
      <>
        <TabSelector
          activeTab={"categoryKeywords"}
          onTabChange={this.handleTabChange}
          className="tab-selector"
        />
        <div className="spacer">
          <button
            onClick={() => this.setActiveTab("categories")}
            className={`button ${
              activeTab === "categories" ? "button--active" : ""
            }`}
          >
            Категории
          </button>
          <button
            onClick={() => this.setActiveTab("keywords")}
            className={`button ${
              activeTab === "keywords" ? "button--active" : ""
            }`}
          >
            Ключевые слова
          </button>
        </div>
        {activeTab === "categories" && (
          <div>
            <div className="spacer">
              <input
                type="text"
                value={newCategory}
                onChange={this.handleCategoryChange}
                placeholder="Новая категория"
                className="custom-input"
              />
              <input
                type="email"
                value={newCategoryEmail}
                onChange={this.handleCategoryEmailChange}
                placeholder="Email"
                className="custom-input-email"
              />
              <button onClick={this.addCategory} className="button">
                Добавить категорию
              </button>
            </div>
            <div>
              <h3>Текущие категории</h3>

              <div className="wrapper-center">
                <ul
                  className="keyword-list"
                  
                >
                  {Object.keys(categories).map((category) => (
                    <li key={category}>
                      {category}
                      <button
                        onClick={() => this.removeCategory(category)}
                        className="remove-button"
                      >
                        &times;
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
        {activeTab === "keywords" && (
          <div>
            <div className="spacer">
              <input
                type="text"
                value={newKeyword}
                onChange={this.handleKeywordChange}
                placeholder="Новое ключевое слово"
                className="custom-input"
              />
              <button onClick={this.addKeyword} className="button">
                Добавить ключевое слово
              </button>
            </div>
            <div className="spacer">
              <input
                type="text"
                value={searchKeyword}
                onChange={this.handleSearchChange}
                placeholder="Поиск ключевых слов"
                className="custom-input"
              />
              <h3>Текущие ключевые слова</h3>

              <div className="wrapper-center">
                <ul
                  className="keyword-list"
                  style={{
                    overflowY:
                      filteredKeywords.length > 10 ? "scroll" : "visible",
                  }}
                >
                  {filteredKeywords.map((keyword, index) => (
                    <li key={index}>
                      {keyword}
                      <button
                        onClick={() => this.removeKeyword(keyword)}
                        className="remove-button"
                      >
                        &times;
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
        <div className="spacer">
          <button onClick={this.saveChanges} className="button">
            Сохранить изменения
          </button>
        </div>
      </>
    );
  }
}

export { CategoryEdit };
