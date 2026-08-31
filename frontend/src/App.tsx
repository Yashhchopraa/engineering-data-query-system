import {
  useCallback,
  useRef,
  useState,
} from "react";

import {
  Box,
  Search,
  RotateCcw,
  MousePointer2,
  Hand,
  Maximize,
  ScanLine,
  List,
  Star,
  FileText,
  Info,
  Hexagon,
  FolderOpen,
  Settings,
  FileBarChart,
  Database,
  User,
  Circle,
  Square,
  Upload,
  Play,
  CheckCircle2,
  Activity,
  Server,
  BarChart3,
  ChevronRight,
} from "lucide-react";

import "./App.css";

import EngineeringViewer from "./components/EngineeringViewer";
import type { ViewerComponent } from "./components/EngineeringViewer";


function App() {

  /* =====================================================
     MAIN NAVIGATION
  ===================================================== */

  const [activePage, setActivePage] =
    useState<
      "explorer" |
      "models" |
      "queries" |
      "reports" |
      "settings"
    >("explorer");


  /* =====================================================
     FILTER STATE
  ===================================================== */

  const [discipline, setDiscipline] =
    useState("");

  const [componentType, setComponentType] =
    useState("");

  const [attributeName, setAttributeName] =
    useState("");

  const [attributeValue, setAttributeValue] =
    useState("");

  const fileInputRef =
    useRef<HTMLInputElement | null>(null);

  const handleImportModel = () => {
    fileInputRef.current?.click();
  };

  const handleModelFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    alert(`Selected model: ${file.name}`);
  };
  /* =====================================================
     MODEL STATE

     IMPORTANT:
     EngineeringViewer is responsible for loading
     components. App receives them through the stable
     callback below.
  ===================================================== */

  const [viewerComponents, setViewerComponents] =
    useState<ViewerComponent[]>([]);

  const [highlightedIds, setHighlightedIds] =
    useState<Set<string>>(new Set());

  const [hasSearched, setHasSearched] =
    useState(false);

  const [selectedComponent, setSelectedComponent] =
    useState<ViewerComponent | null>(null);


  /* =====================================================
     VIEWER STATE
  ===================================================== */

  const [zoom, setZoom] =
    useState(100);

  const [viewerMode, setViewerMode] =
    useState<"select" | "pan">("select");

  const [resetViewSignal, setResetViewSignal] =
    useState(0);

  const [fitViewSignal, setFitViewSignal] =
    useState(0);


  /* =====================================================
     TAB STATE
  ===================================================== */

  const [activeTab, setActiveTab] =
    useState<
      "results" |
      "recommendations" |
      "details"
    >("results");


  /* =====================================================
     IMPORTANT FIX

     This callback has a stable reference.

     DO NOT define this directly inside JSX.
  ===================================================== */

  const handleComponentsLoaded = useCallback(
    (components: ViewerComponent[]) => {

      setViewerComponents(components);

    },
    []
  );


  /* =====================================================
     FILTERED SEARCH RESULTS
  ===================================================== */

  const filteredComponents =
    viewerComponents.filter(
      (component) =>
        highlightedIds.has(
          component.component_id
        )
    );


  /* =====================================================
     SELECT COMPONENT
  ===================================================== */

  const handleViewerComponentSelect =
    useCallback(
      (component: ViewerComponent) => {

        setSelectedComponent(component);

        setActiveTab("details");

      },
      []
    );


  /* =====================================================
     SEARCH COMPONENTS
  ===================================================== */

  const searchComponents = async () => {

    setHasSearched(true);

    setSelectedComponent(null);

    setActiveTab("results");


    try {

      const params =
        new URLSearchParams();


      if (discipline) {

        params.append(
          "discipline",
          discipline
        );

      }


      if (componentType) {

        params.append(
          "component_type",
          componentType
        );

      }


      if (
        attributeName &&
        attributeValue
      ) {

        params.append(
          "attribute_name",
          attributeName
        );

        params.append(
          "attribute_value",
          attributeValue
        );

      }


      const response =
        await fetch(
          `http://127.0.0.1:8000/api/query?${params.toString()}`
        );


      if (!response.ok) {

        throw new Error(
          `Query failed: ${response.status}`
        );

      }


      const data =
        await response.json();


      const ids =
        new Set<string>(
          data.component_ids ?? []
        );


      setHighlightedIds(ids);


    } catch (error) {

      console.error(
        "Failed to query components:",
        error
      );

      setHighlightedIds(
        new Set()
      );

    }

  };


  /* =====================================================
     CLEAR FILTERS
  ===================================================== */

  const clearFilters = () => {

    setDiscipline("");

    setComponentType("");

    setAttributeName("");

    setAttributeValue("");

    setHasSearched(false);

    setHighlightedIds(
      new Set()
    );

    setSelectedComponent(null);

    setActiveTab("results");

  };


  /* =====================================================
     FULLSCREEN
  ===================================================== */

  const toggleFullscreen = () => {

    const viewer =
      document.querySelector(
        ".viewer-panel"
      ) as HTMLElement | null;


    if (!viewer) {
      return;
    }


    if (document.fullscreenElement) {

      document.exitFullscreen();

    } else {

      viewer.requestFullscreen();

    }

  };


  /* =====================================================
     SELECT RESULT
  ===================================================== */

  const selectResult = (
    component: ViewerComponent
  ) => {

    setSelectedComponent(component);

    setActiveTab("details");

  };


  /* =====================================================
     NAVIGATION
  ===================================================== */

  const navigateTo = (
    page:
      | "explorer"
      | "models"
      | "queries"
      | "reports"
      | "settings"
  ) => {

    setActivePage(page);

  };


  /* =====================================================
     NAV BUTTON
  ===================================================== */

  const NavigationButton = ({
    page,
    icon,
    label,
  }: {
    page:
      | "explorer"
      | "models"
      | "queries"
      | "reports"
      | "settings";

    icon: React.ReactNode;

    label: string;
  }) => (

    <button
      type="button"
      className={
        `nav-item ${
          activePage === page
            ? "active"
            : ""
        }`
      }
      onClick={() =>
        navigateTo(page)
      }
    >

      {icon}

      <span>
        {label}
      </span>

    </button>

  );


  /* =====================================================
     SHARED HEADER
  ===================================================== */

  const renderHeader = () => (

    <header className="topbar">

      <div className="brand">

        <div className="brand-icon">

          <Hexagon
            size={24}
            strokeWidth={1.8}
          />

        </div>


        <div className="brand-text">

          <h1>
            Engineering Data Explorer
          </h1>

          <span>
            Component Query & Visualization System
          </span>

        </div>

      </div>


      <nav className="navigation">

        <NavigationButton
          page="explorer"
          icon={<Box size={17} />}
          label="Explorer"
        />

        <NavigationButton
          page="models"
          icon={<Database size={17} />}
          label="Models"
        />

        <NavigationButton
          page="queries"
          icon={<Search size={17} />}
          label="Queries"
        />

        <NavigationButton
          page="reports"
          icon={<FileBarChart size={17} />}
          label="Reports"
        />

        <NavigationButton
          page="settings"
          icon={<Settings size={17} />}
          label="Settings"
        />

      </nav>


      <div className="topbar-right">

        <div className="api-status">

          <span className="status-dot" />

          API Connected

        </div>


        <button
          className="profile-button"
          type="button"
        >

          <User size={20} />

        </button>

      </div>

    </header>

  );


  /* =====================================================
     FOOTER
  ===================================================== */

  const renderFooter = () => (

    <footer className="footer">

      <div className="footer-left">

        <span>
          Project: Sample Project
        </span>

        <div className="footer-separator" />

        <span>
          Model: Engineering Sample
        </span>

        <div className="footer-separator" />

        <span>
          Components:{" "}
          {viewerComponents.length}
        </span>

      </div>


      <span>
        v1.0.0
      </span>

    </footer>

  );


  /* =====================================================
     MODELS PAGE
  ===================================================== */

  const renderModelsPage = () => (

    <main className="management-page">

      <div className="page-eyebrow">
        MODEL MANAGEMENT
      </div>

      <div className="page-heading-row">

        <div>

          <h2>
            Models
          </h2>

          <p>
            Manage engineering models available
            to the explorer.
          </p>

        </div>


        <button
          type="button"
          className="primary-action"
          onClick={handleImportModel}
        >
          <Upload size={16} />
          Import Model
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept=".db,.sqlite,.sqlite3"
          style={{ display: "none" }}
          onChange={handleModelFileChange}
        />

      </div>


      <section className="management-section">

        <div className="section-title-row">

          <div>

            <h3>
              Engineering Models
            </h3>

            <p>
              Available engineering data sources
            </p>

          </div>

        </div>


        <div className="model-card-grid">


          <div className="model-card active-model">

            <div className="model-card-top">

              <div className="model-icon">

                <Database size={22} />

              </div>


              <span className="status-badge active">

                <CheckCircle2 size={13} />

                Active

              </span>

            </div>


            <h3>
              Engineering Sample
            </h3>

            <p>
              Sample Project
            </p>


            <div className="model-meta">

              <span>
                <Database size={14} />
                {viewerComponents.length} components
              </span>

              <span>
                SQLite
              </span>

              <span>
                Connected
              </span>

            </div>


            <button
              type="button"
              className="model-action"
              onClick={() =>
                navigateTo("explorer")
              }
            >

              Open Explorer

              <ChevronRight size={16} />

            </button>

          </div>


          <div className="model-card">

            <div className="model-card-top">

              <div className="model-icon">

                <Database size={22} />

              </div>


              <span className="status-badge">

                Not Loaded

              </span>

            </div>


            <h3>
              Engineering Sample 2
            </h3>

            <p>
              Additional engineering model
            </p>


            <div className="model-meta">

              <span>
                Model available
              </span>

              <span>
                SQLite
              </span>

            </div>


            <button
              type="button"
              className="secondary-action"
              onClick={() => {

                alert(
                  "Model loading will be connected to the backend model-management API."
                );

              }}
            >

              <Play size={15} />

              Load Model

            </button>

          </div>


          <div className="model-card import-card">

            <div className="import-card-icon">

              <Upload size={24} />

            </div>

            <h3>
              Import Model
            </h3>

            <p>
              Add another engineering model
              or SQLite model source.
            </p>


            <button
              type="button"
              className="secondary-action"
              onClick={() => {

                alert(
                  "Model import will be connected to the backend import API."
                );

              }}
            >

              <Upload size={15} />

              Import

            </button>

          </div>

        </div>

      </section>


      <section className="management-section current-model-section">

        <div className="section-title-row">

          <div>

            <h3>
              Current Model
            </h3>

            <p>
              Active engineering model
            </p>

          </div>

          <div className="connection-pill">

            <span className="status-dot" />

            Connected

          </div>

        </div>


        <div className="current-model-card">

          <div className="current-model-icon">

            <Database size={25} />

          </div>


          <div className="current-model-info">

            <h3>
              Engineering Sample
            </h3>

            <p>
              Connected to Explorer
            </p>

          </div>


          <div className="current-model-stats">

            <div>

              <strong>
                {viewerComponents.length}
              </strong>

              <span>
                Components
              </span>

            </div>


            <div>

              <strong>
                SQLite
              </strong>

              <span>
                Data Source
              </span>

            </div>

          </div>

        </div>

      </section>

    </main>

  );


  /* =====================================================
     QUERIES PAGE
  ===================================================== */

  const renderQueriesPage = () => (

    <main className="management-page">

      <div className="page-eyebrow">
        QUERY MANAGEMENT
      </div>


      <div className="page-heading-row">

        <div>

          <h2>
            Queries
          </h2>

          <p>
            Run, review and manage engineering
            component queries.
          </p>

        </div>


        <button
          type="button"
          className="primary-action"
          onClick={() =>
            navigateTo("explorer")
          }
        >

          <Search size={17} />

          New Query

        </button>

      </div>


      <div className="query-summary-grid">

        <div className="summary-card">

          <div className="summary-icon">

            <Search size={19} />

          </div>

          <div>

            <span>
              Current Results
            </span>

            <strong>
              {hasSearched
                ? filteredComponents.length
                : 0}
            </strong>

          </div>

        </div>


        <div className="summary-card">

          <div className="summary-icon">

            <Database size={19} />

          </div>

          <div>

            <span>
              Components Indexed
            </span>

            <strong>
              {viewerComponents.length}
            </strong>

          </div>

        </div>


        <div className="summary-card">

          <div className="summary-icon">

            <Activity size={19} />

          </div>

          <div>

            <span>
              Query Status
            </span>

            <strong>
              Ready
            </strong>

          </div>

        </div>

      </div>


      <section className="empty-management-card">

        <div className="large-empty-icon">

          <Search size={30} />

        </div>

        <h3>
          No saved queries yet
        </h3>

        <p>
          Create a query from the Explorer
          using the query builder.
        </p>


        <button
          type="button"
          className="primary-action"
          onClick={() =>
            navigateTo("explorer")
          }
        >

          <Box size={16} />

          Go to Explorer

        </button>

      </section>

    </main>

  );


  /* =====================================================
     REPORTS PAGE
  ===================================================== */

  const renderReportsPage = () => (

    <main className="management-page">

      <div className="page-eyebrow">
        ANALYTICS
      </div>


      <div className="page-heading-row">

        <div>

          <h2>
            Reports
          </h2>

          <p>
            Review engineering model and
            query information.
          </p>

        </div>


        <button
          type="button"
          className="primary-action"
          onClick={() => {

            alert(
              "Report export will be connected to the backend reporting service."
            );

          }}
        >

          <FileBarChart size={17} />

          Export Report

        </button>

      </div>


      <div className="report-stat-grid">

        <div className="report-stat-card">

          <div className="report-stat-icon">

            <Database size={19} />

          </div>

          <span>
            Total Components
          </span>

          <strong>
            {viewerComponents.length}
          </strong>

          <small>
            Current engineering model
          </small>

        </div>


        <div className="report-stat-card">

          <div className="report-stat-icon">

            <CheckCircle2 size={19} />

          </div>

          <span>
            Model Status
          </span>

          <strong>
            Active
          </strong>

          <small>
            Engineering Sample
          </small>

        </div>


        <div className="report-stat-card">

          <div className="report-stat-icon">

            <Search size={19} />

          </div>

          <span>
            Query Matches
          </span>

          <strong>
            {hasSearched
              ? filteredComponents.length
              : 0}
          </strong>

          <small>
            Latest query
          </small>

        </div>


        <div className="report-stat-card">

          <div className="report-stat-icon">

            <Server size={19} />

          </div>

          <span>
            API Status
          </span>

          <strong>
            Connected
          </strong>

          <small>
            Backend available
          </small>

        </div>

      </div>


      <div className="report-grid">


        <section className="report-card">

          <div className="report-card-header">

            <div>

              <h3>
                Model Summary
              </h3>

              <p>
                Component counts and model overview
              </p>

            </div>

            <BarChart3 size={20} />

          </div>


          <div className="report-details">

            <div>
              <span>
                Components loaded
              </span>

              <strong>
                {viewerComponents.length}
              </strong>
            </div>


            <div>
              <span>
                Current project
              </span>

              <strong>
                Sample Project
              </strong>
            </div>


            <div>
              <span>
                Model
              </span>

              <strong>
                Engineering Sample
              </strong>
            </div>


            <div>
              <span>
                Data source
              </span>

              <strong>
                SQLite
              </strong>
            </div>

          </div>

        </section>


        <section className="report-card">

          <div className="report-card-header">

            <div>

              <h3>
                Query Report
              </h3>

              <p>
                Summary of the current component query
              </p>

            </div>

            <Search size={20} />

          </div>


          <div className="query-report-body">

            {!hasSearched ? (

              <>

                <strong>
                  No query has been executed
                </strong>

                <p>
                  Run a query from the Explorer
                  to generate results.
                </p>


                <button
                  type="button"
                  className="secondary-action"
                  onClick={() =>
                    navigateTo("explorer")
                  }
                >

                  <Search size={15} />

                  Run Query

                </button>

              </>

            ) : (

              <>

                <strong>
                  {filteredComponents.length}
                  {" "}
                  matching components
                </strong>

                <p>
                  The latest query returned
                  matching engineering components.
                </p>


                <button
                  type="button"
                  className="secondary-action"
                  onClick={() =>
                    navigateTo("explorer")
                  }
                >

                  View Results

                  <ChevronRight size={15} />

                </button>

              </>

            )}

          </div>

        </section>


        <section className="report-card">

          <div className="report-card-header">

            <div>

              <h3>
                Data Overview
              </h3>

              <p>
                Engineering model data availability
              </p>

            </div>

            <Activity size={20} />

          </div>


          <div className="data-overview">

            <div className="data-progress-header">

              <span>
                Components
              </span>

              <strong>
                {viewerComponents.length}
              </strong>

            </div>


            <div className="data-progress">

              <div
                className="data-progress-fill"
                style={{
                  width:
                    viewerComponents.length > 0
                      ? "100%"
                      : "0%",
                }}
              />

            </div>


            <div className="data-progress-footer">

              <span>
                Model availability
              </span>

              <strong>
                {viewerComponents.length > 0
                  ? "100%"
                  : "0%"}
              </strong>

            </div>

          </div>

        </section>

      </div>

    </main>

  );


  /* =====================================================
     SETTINGS PAGE
  ===================================================== */

  const renderSettingsPage = () => (

    <main className="management-page">

      <div className="page-eyebrow">
        CONFIGURATION
      </div>


      <div className="page-heading-row">

        <div>

          <h2>
            Settings
          </h2>

          <p>
            View application and connection
            configuration.
          </p>

        </div>

      </div>


      <div className="settings-grid">


        <section className="settings-card">

          <div className="settings-card-header">

            <div className="settings-icon">

              <Server size={20} />

            </div>

            <div>

              <h3>
                API Connection
              </h3>

              <p>
                Backend engineering data API
              </p>

            </div>

          </div>


          <div className="connection-status-large">

            <CheckCircle2 size={19} />

            <div>

              <strong>
                Connected
              </strong>

              <span>
                Backend API is responding
              </span>

            </div>

          </div>


          <div className="settings-detail">

            <span>
              API Endpoint
            </span>

            <strong>
              http://127.0.0.1:8000
            </strong>

          </div>


          <button
            type="button"
            className="secondary-action"
            onClick={() =>
              window.location.reload()
            }
          >

            <RotateCcw size={15} />

            Test Connection

          </button>

        </section>


        <section className="settings-card">

          <div className="settings-card-header">

            <div className="settings-icon">

              <Database size={20} />

            </div>

            <div>

              <h3>
                Current Model
              </h3>

              <p>
                Currently loaded engineering model
              </p>

            </div>

          </div>


          <div className="settings-model">

            <div className="settings-model-icon">

              <Database size={22} />

            </div>


            <div>

              <strong>
                Engineering Sample
              </strong>

              <span>
                {viewerComponents.length}
                {" "}
                components loaded
              </span>

            </div>


            <span className="status-badge active">

              Active

            </span>

          </div>

        </section>


        <section className="settings-card">

          <div className="settings-card-header">

            <div className="settings-icon">

              <Settings size={20} />

            </div>

            <div>

              <h3>
                Application
              </h3>

              <p>
                Engineering Data Explorer configuration
              </p>

            </div>

          </div>


          <div className="settings-list">

            <div>

              <span>
                Application Version
              </span>

              <strong>
                v1.0.0
              </strong>

            </div>


            <div>

              <span>
                Viewer Mode
              </span>

              <strong>
                {viewerMode === "select"
                  ? "Select"
                  : "Pan"}
              </strong>

            </div>


            <div>

              <span>
                Minimap
              </span>

              <strong>
                Enabled
              </strong>

            </div>


            <div>

              <span>
                API Status
              </span>

              <strong>
                Connected
              </strong>

            </div>

          </div>

        </section>


        <section className="settings-card">

          <div className="settings-card-header">

            <div className="settings-icon">

              <Info size={20} />

            </div>

            <div>

              <h3>
                Configuration
              </h3>

              <p>
                Advanced application configuration
              </p>

            </div>

          </div>


          <div className="settings-placeholder">

            <Info size={22} />

            <p>
              Advanced configuration options can
              be connected here as the application
              backend grows.
            </p>

          </div>

        </section>

      </div>

    </main>

  );


  /* =====================================================
     EXPLORER PAGE
  ===================================================== */

  const renderExplorerPage = () => (

    <main className="workspace">


      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside className="sidebar">

        <div className="sidebar-header">

          <h2>
            Query Builder
          </h2>

          <p>
            Filter engineering components
          </p>

        </div>


        <div className="filter-section">

          <label>
            DISCIPLINE
          </label>

          <select
            value={discipline}
            onChange={(event) =>
              setDiscipline(
                event.target.value
              )
            }
          >

            <option value="">
              All disciplines
            </option>

            <option value="Piping">
              Piping
            </option>

            <option value="Structural">
              Structural
            </option>

            <option value="Electrical">
              Electrical
            </option>

            <option value="Equipment">
              Equipment
            </option>

            <option value="HVAC">
              HVAC
            </option>

          </select>

        </div>


        <div className="filter-section">

          <label>
            COMPONENT TYPE
          </label>

          <input
            type="text"
            placeholder="e.g. valve, pipe..."
            value={componentType}
            onChange={(event) =>
              setComponentType(
                event.target.value
              )
            }
          />

        </div>


        <div className="filter-section">

          <label>
            ATTRIBUTE NAME
          </label>

          <input
            type="text"
            placeholder="e.g. status"
            value={attributeName}
            onChange={(event) =>
              setAttributeName(
                event.target.value
              )
            }
          />

        </div>


        <div className="filter-section">

          <label>
            ATTRIBUTE VALUE
          </label>

          <input
            type="text"
            placeholder="e.g. installed"
            value={attributeValue}
            onChange={(event) =>
              setAttributeValue(
                event.target.value
              )
            }
          />

        </div>


        <button
          className="search-button"
          type="button"
          onClick={searchComponents}
        >

          <Search size={18} />

          Search Components

        </button>


        <button
          className="clear-button"
          type="button"
          onClick={clearFilters}
        >

          <RotateCcw size={17} />

          Clear Filters

        </button>


        <div className="sidebar-divider" />


        <div className="query-status">

          <span className="ready-dot" />

          {hasSearched
            ? `${filteredComponents.length} components found`
            : `${viewerComponents.length} components loaded`
          }

        </div>


        <div className="tip-box">

          <Info size={17} />

          <p>

            <strong>
              Tip:
            </strong>

            {" "}
            Use filters to narrow down
            components in the model.

          </p>

        </div>

      </aside>


      {/* =================================================
          MAIN CONTENT
      ================================================= */}

      <section className="content">


        {/* =================================================
            ENGINEERING VIEWER
        ================================================= */}

        <section className="viewer-panel">

          <div className="viewer-header">

            <div>

              <h2>
                Engineering Model
              </h2>

              <p>
                Interactive component visualization
              </p>

            </div>


            <div className="viewer-actions">


              <div className="tool-group">

                <button
                  type="button"
                  className={
                    `tool-button ${
                      viewerMode === "select"
                        ? "active-tool"
                        : ""
                    }`
                  }
                  onClick={() =>
                    setViewerMode("select")
                  }
                  title="Select"
                >

                  <MousePointer2
                    size={18}
                  />

                </button>


                <button
                  type="button"
                  className={
                    `tool-button ${
                      viewerMode === "pan"
                        ? "active-tool"
                        : ""
                    }`
                  }
                  onClick={() =>
                    setViewerMode("pan")
                  }
                  title="Pan"
                >

                  <Hand
                    size={18}
                  />

                </button>


                <button
                  type="button"
                  className="tool-button"
                  onClick={
                    toggleFullscreen
                  }
                  title="Fullscreen"
                >

                  <Maximize
                    size={18}
                  />

                </button>

              </div>


              <div className="viewer-divider" />


              <button
                type="button"
                className="viewer-button"
                onClick={() => {

                  setZoom(100);

                  setFitViewSignal(
                    (value) =>
                      value + 1
                  );

                }}
              >

                <ScanLine
                  size={17}
                />

                Fit View

              </button>


              <button
                type="button"
                className="viewer-button"
                onClick={() => {

                  setZoom(100);

                  setSelectedComponent(
                    null
                  );

                  setViewerMode(
                    "select"
                  );

                  setActiveTab(
                    "results"
                  );

                  setResetViewSignal(
                    (value) =>
                      value + 1
                  );

                }}
              >

                <RotateCcw
                  size={17}
                />

                Reset

              </button>

            </div>

          </div>


          <div className="model-canvas">

            <EngineeringViewer

              highlightedIds={
                highlightedIds
              }

              hasSearched={
                hasSearched
              }

              selectedComponentId={
                selectedComponent
                  ?.component_id ?? null
              }

              onSelectComponent={
                handleViewerComponentSelect
              }

              onComponentsLoaded={
                handleComponentsLoaded
              }

              zoom={
                zoom / 100
              }

              viewerMode={
                viewerMode
              }

              resetViewSignal={
                resetViewSignal
              }

              fitViewSignal={
                fitViewSignal
              }

            />


            {selectedComponent && (

              <div className="component-tooltip">

                <strong>
                  {
                    selectedComponent
                      .component_id
                  }
                </strong>

                <span>
                  Type:{" "}
                  {
                    selectedComponent
                      .component_type
                  }
                </span>

                <span>
                  Discipline:{" "}
                  {
                    selectedComponent
                      .discipline
                  }
                </span>

                <span>
                  Zone:{" "}
                  {
                    selectedComponent
                      .zone
                  }
                </span>

              </div>

            )}


            <div className="mini-map">

              <div className="mini-map-box">

                {viewerComponents.map(
                  (component) => {

                    const geometry =
                      component.geometry;

                    const highlighted =
                      hasSearched &&
                      highlightedIds.has(
                        component.component_id
                      );


                    return (

                      <span
                        key={
                          component.component_id
                        }

                        className={
                          highlighted
                            ? "mini-highlight"
                            : ""
                        }

                        style={{
                          left:
                            `${geometry.x / 6}px`,

                          top:
                            `${geometry.y / 6}px`,
                        }}

                      />

                    );

                  }
                )}

              </div>


              <div className="zoom-controls">

                <button
                  type="button"
                  aria-label="Zoom out"
                  onClick={() =>
                    setZoom(
                      (current) =>
                        Math.max(
                          50,
                          current - 10
                        )
                    )
                  }
                >

                  −

                </button>


                <span>
                  {zoom}%
                </span>


                <button
                  type="button"
                  aria-label="Zoom in"
                  onClick={() =>
                    setZoom(
                      (current) =>
                        Math.min(
                          150,
                          current + 10
                        )
                    )
                  }
                >

                  +

                </button>

              </div>

            </div>

          </div>

        </section>


        {/* =================================================
            RESULTS PANEL
        ================================================= */}

        <section className="results-panel">


          <div className="tabs">

            <button
              type="button"
              className={
                `tab ${
                  activeTab === "results"
                    ? "active-tab"
                    : ""
                }`
              }
              onClick={() =>
                setActiveTab("results")
              }
            >

              <List size={15} />

              <span>
                Results
              </span>

            </button>


            <button
              type="button"
              className={
                `tab ${
                  activeTab === "recommendations"
                    ? "active-tab"
                    : ""
                }`
              }
              onClick={() =>
                setActiveTab(
                  "recommendations"
                )
              }
            >

              <Star size={15} />

              <span>
                Recommendations
              </span>

            </button>


            <button
              type="button"
              className={
                `tab ${
                  activeTab === "details"
                    ? "active-tab"
                    : ""
                }`
              }
              onClick={() =>
                setActiveTab("details")
              }
            >

              <FileText size={15} />

              <span>
                Component Details
              </span>

            </button>

          </div>


          {/* RESULTS */}

          {activeTab === "results" && (

            <div className="results-content">

              {!hasSearched && (

                <div className="empty-results">

                  <div className="results-icon">

                    <FolderOpen
                      size={38}
                      strokeWidth={1.5}
                    />

                  </div>

                  <h3>
                    No Results Yet
                  </h3>

                  <p>
                    Run a query to view
                    matching components.
                  </p>

                </div>

              )}


              {hasSearched &&
                filteredComponents.length === 0 && (

                <div className="empty-results">

                  <Search
                    size={38}
                    strokeWidth={1.5}
                  />

                  <h3>
                    No Matching Components
                  </h3>

                  <p>
                    Try modifying your filters.
                  </p>

                </div>

              )}


              {hasSearched &&
                filteredComponents.length > 0 && (

                <div className="results-list">

                  {filteredComponents.map(
                    (component) => (

                      <button
                        type="button"
                        key={
                          component.component_id
                        }

                        className={
                          `result-item ${
                            selectedComponent
                              ?.component_id ===
                            component.component_id
                              ? "selected-result"
                              : ""
                          }`
                        }

                        onClick={() =>
                          selectResult(
                            component
                          )
                        }
                      >

                        <div className="result-icon">

                          {
                            component
                              .geometry
                              .geometry_type
                              .toLowerCase() ===
                            "circle"
                              ? (
                                <Circle
                                  size={15}
                                />
                              )
                              : (
                                <Square
                                  size={15}
                                />
                              )
                          }

                        </div>


                        <div className="result-info">

                          <strong>
                            {
                              component
                                .component_id
                            }
                          </strong>

                          <span>

                            {
                              component
                                .component_type
                            }

                            {" • "}

                            {
                              component
                                .discipline
                            }

                            {" • "}

                            {
                              component
                                .zone
                            }

                          </span>

                        </div>

                      </button>

                    )
                  )}

                </div>

              )}

            </div>

          )}


          {/* RECOMMENDATIONS */}

          {activeTab === "recommendations" && (

            <div className="results-content">

              <div className="tab-placeholder">

                <div className="tab-placeholder-icon">

                  <Star
                    size={28}
                    strokeWidth={1.6}
                  />

                </div>

                <h3>
                  Recommendations
                </h3>

                <p>
                  Recommendations will appear
                  here once the query intelligence
                  layer is connected.
                </p>

              </div>

            </div>

          )}


          {/* DETAILS */}

          {activeTab === "details" && (

            <div className="results-content">

              {!selectedComponent && (

                <div className="empty-results">

                  <FileText
                    size={38}
                    strokeWidth={1.5}
                  />

                  <h3>
                    No Component Selected
                  </h3>

                  <p>
                    Select a component from
                    the model or results.
                  </p>

                </div>

              )}


              {selectedComponent && (

                <div className="component-details">

                  <div className="details-header">

                    <div>

                      <span className="details-eyebrow">
                        COMPONENT
                      </span>

                      <h3>
                        {
                          selectedComponent
                            .component_id
                        }
                      </h3>

                    </div>

                  </div>


                  <div className="details-divider" />


                  <div className="details-grid">


                    <div className="detail-field">

                      <span>
                        Component ID
                      </span>

                      <strong>
                        {
                          selectedComponent
                            .component_id
                        }
                      </strong>

                    </div>


                    <div className="detail-field">

                      <span>
                        Component Type
                      </span>

                      <strong>
                        {
                          selectedComponent
                            .component_type
                        }
                      </strong>

                    </div>


                    <div className="detail-field">

                      <span>
                        Discipline
                      </span>

                      <strong>
                        {
                          selectedComponent
                            .discipline
                        }
                      </strong>

                    </div>


                    <div className="detail-field">

                      <span>
                        Zone
                      </span>

                      <strong>
                        {
                          selectedComponent
                            .zone
                        }
                      </strong>

                    </div>


                    <div className="detail-field">

                      <span>
                        Geometry
                      </span>

                      <strong>
                        {
                          selectedComponent
                            .geometry
                            .geometry_type
                        }
                      </strong>

                    </div>


                    <div className="detail-field">

                      <span>
                        Position
                      </span>

                      <strong>

                        {
                          Math.round(
                            selectedComponent
                              .geometry
                              .x
                          )
                        }

                        {" , "}

                        {
                          Math.round(
                            selectedComponent
                              .geometry
                              .y
                          )
                        }

                      </strong>

                    </div>


                    <div className="detail-field">

                      <span>
                        Width
                      </span>

                      <strong>
                        {
                          Math.round(
                            selectedComponent
                              .geometry
                              .width
                          )
                        }
                      </strong>

                    </div>


                    <div className="detail-field">

                      <span>
                        Height
                      </span>

                      <strong>
                        {
                          Math.round(
                            selectedComponent
                              .geometry
                              .height
                          )
                        }
                      </strong>

                    </div>


                    <div className="detail-field">

                      <span>
                        Rotation
                      </span>

                      <strong>
                        {
                          Math.round(
                            selectedComponent
                              .geometry
                              .rotation
                          )
                        }°
                      </strong>

                    </div>


                  </div>

                </div>

              )}

            </div>

          )}

        </section>

      </section>

    </main>

  );


  /* =====================================================
     PAGE CONTENT
  ===================================================== */

  const renderPage = () => {

    switch (activePage) {

      case "models":
        return renderModelsPage();

      case "queries":
        return renderQueriesPage();

      case "reports":
        return renderReportsPage();

      case "settings":
        return renderSettingsPage();

      case "explorer":
      default:
        return renderExplorerPage();

    }

  };


  /* =====================================================
     RENDER APP
  ===================================================== */

  return (

    <div className="app">

      {renderHeader()}

      {renderPage()}

      {renderFooter()}

    </div>

  );

}

export default App;