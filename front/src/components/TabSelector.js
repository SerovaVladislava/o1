const TabSelector = ({ activeTab }) => {
  const handleTabChange = (tab) => {
    if (tab === "dataProcessing") {
      window.location.href = "/";
    } else if (tab === "categoryKeywords") {
      window.location.href = "/category-edit";
    } else if (tab === "sendEmail") {
      window.location.href = "/send-email"; // Новый маршрут для рассылки по почте
    }
  };

  return (
    <div className="tab-selector">
      <button
        onClick={() => handleTabChange("dataProcessing")}
        className={`button ${
          activeTab === "dataProcessing" ? "button--active" : "button--inactive"
        }`}
      >
        Обработка данных
      </button>
      <button
        onClick={() => handleTabChange("categoryKeywords")}
        className={`button ${
          activeTab === "categoryKeywords"
            ? "button--active"
            : "button--inactive"
        }`}
      >
        Изменение категорий и ключевых слов
      </button>
      <button
        onClick={() => handleTabChange("sendEmail")}
        className={`button ${
          activeTab === "sendEmail" ? "button--active" : "button--inactive"
        }`}
      >
        Рассылка по почте
      </button>
    </div>
  );
};

export default TabSelector;
