# NeuralStark Canvas Documentation

This document explains how to use the `canvas` JSON object returned by the `/chat` endpoint to render dynamic, data-driven UI components in your frontend application.

## 1. The Canvas Concept

The `canvas` object is a structured JSON representation of a UI layout. Instead of returning a static image or a fixed HTML block, the API provides a blueprint of components that the frontend can render natively. This allows for greater flexibility, interactivity, and consistency with your application's design system.

The basic structure of a canvas response is:

```json
{
  "response": {
    "canvas": {
      "type": "container",
      "layout": "vertical",
      "children": [
        // ... array of component objects ...
      ]
    }
  }
}
```

## 2. How to Parse and Render the Canvas

Your frontend application should have a central `CanvasRenderer` component. This component's responsibility is to:

1.  Receive the `canvas` JSON object as a prop.
2.  Iterate through the `children` array.
3.  For each child object, look at its `type` property.
4.  Render the corresponding native frontend component based on the `type`.

### Example: React `CanvasRenderer`

Here is a conceptual example of how you might implement this in React:

```jsx
// CanvasRenderer.jsx
import React from 'react';
import KpiDashboard from './components/KpiDashboard';
import BarChart from './components/BarChart';
import Header from './components/Header';
import KeyValuePairs from './components/KeyValuePairs';

const componentMapping = {
  kpi_dashboard: KpiDashboard,
  bar_chart: BarChart,
  header: Header,
  key_value_pairs: KeyValuePairs,
  // ... add other component mappings here
};

const CanvasRenderer = ({ canvasData }) => {
  if (!canvasData || !canvasData.children) {
    return null;
  }

  return (
    <div className={`canvas-container layout-${canvasData.layout || 'vertical'}`}>
      {canvasData.children.map((component, index) => {
        const Component = componentMapping[component.type];
        if (Component) {
          return <Component key={index} {...component} />;
        }
        return <div key={index}>Unsupported component type: {component.type}</div>;
      })}
    </div>
  );
};

export default CanvasRenderer;
```

## 3. Dynamism of the Data

The AI agent will populate the `data` field of the chosen template with the information it retrieves from the knowledge base or generates itself. The `title`, `config`, and `axes` fields will generally be taken from the template, but the AI can also override these if necessary.

For example, if the AI generates a `bar_chart`, it will provide the `data` array with the categories and values. The frontend should be prepared to receive this dynamic data and render the chart accordingly.

## 4. Supported Component Types & Schemas

Below are the schemas for the component types currently supported by the `CanvasGenerator` tool. Your frontend should have a corresponding component for each type you wish to render.

### `line_chart`

*   **Description:** A standard line chart, can contain multiple series.
*   **JSON Schema:**
    ```json
    {
      "type": "line_chart",
      "title": "Évolution du CA Trimestriel",
      "config": { /* ... */ },
      "axes": { /* ... */ },
      "data": [
        {
          "series": "CA Réalisé",
          "color": "#2E7D32",
          "points": [
            {"x": "2024-Q1", "y": 1250000}
            // ... more points
          ]
        }
      ]
    }
    ```

### `bar_chart`

*   **Description:** A standard bar chart.
*   **JSON Schema:**
    ```json
    {
      "type": "bar_chart",
      "title": "Performance des Équipes Commerciales",
      "orientation": "vertical",
      "config": { /* ... */ },
      "axes": { /* ... */ },
      "data": [
        {"category": "Équipe Nord", "value": 450, "color": "#FF6B6B"}
        // ... more data objects
      ]
    }
    ```

### `pie_chart`

*   **Description:** A standard pie chart.
*   **JSON Schema:**
    ```json
    {
      "type": "pie_chart",
      "title": "Répartition du Budget Marketing",
      "config": { /* ... */ },
      "data": [
        {"label": "Digital", "value": 45, "color": "#FF6B6B"}
        // ... more data objects
      ]
    }
    ```

### `donut_chart`

*   **Description:** A donut chart.
*   **JSON Schema:**
    ```json
    {
      "type": "donut_chart",
      "title": "Satisfaction Client par Segment",
      "config": { /* ... */ },
      "data": [
        {"label": "Très satisfait", "value": 42, "color": "#4CAF50"}
        // ... more data objects
      ]
    }
    ```

### `area_chart`

*   **Description:** A standard area chart, can be stacked.
*   **JSON Schema:**
    ```json
    {
      "type": "area_chart",
      "title": "Évolution des Revenus par Produit",
      "config": { /* ... */ },
      "axes": { /* ... */ },
      "data": [
        {
          "series": "Produit A",
          "color": "#2196F3",
          "points": [
            {"x": "2024-01", "y": 50000}
            // ... more points
          ]
        }
      ]
    }
    ```

### `scatter_plot`

*   **Description:** A scatter plot, can be used as a bubble chart.
*   **JSON Schema:**
    ```json
    {
      "type": "scatter_plot",
      "title": "Relation Prix vs Performance",
      "config": { /* ... */ },
      "axes": { /* ... */ },
      "data": [
        {"x": 150, "y": 85, "label": "Produit A", "market_share": 25, "color": "#FF6B6B"}
        // ... more data objects
      ]
    }
    ```

### `heatmap`

*   **Description:** A heatmap.
*   **JSON Schema:**
    ```json
    {
      "type": "heatmap",
      "title": "Performance Commerciale par Région/Mois",
      "config": { /* ... */ },
      "axes": { /* ... */ },
      "data": [
        {"x": 0, "y": 0, "value": 85, "label": "Jan-Nord"}
        // ... more data objects
      ]
    }
    ```

### `gauge_chart`

*   **Description:** A gauge chart for displaying a value within a range.
*   **JSON Schema:**
    ```json
    {
      "type": "gauge_chart",
      "title": "Taux de Conversion",
      "config": { /* ... */ },
      "data": {
        "current_value": 68.5,
        "target": 75,
        "zones": [ /* ... */ ]
      }
    }
    ```

### `waterfall_chart`

*   **Description:** A waterfall chart for showing cumulative effects.
*   **JSON Schema:**
    ```json
    {
      "type": "waterfall_chart",
      "title": "Évolution du Budget Q4",
      "config": { /* ... */ },
      "data": [
        {"label": "Budget Initial", "value": 100000, "type": "initial", "color": "#2196F3"}
        // ... more data objects
      ]
    }
    ```

### `funnel_chart`

*   **Description:** A funnel chart for showing stages in a process.
*   **JSON Schema:**
    ```json
    {
      "type": "funnel_chart",
      "title": "Tunnel de Conversion Ventes",
      "config": { /* ... */ },
      "data": [
        {"stage": "Visiteurs", "value": 10000, "color": "#2196F3"}
        // ... more data objects
      ]
    }
    ```

### `radar_chart`

*   **Description:** A radar chart for comparing multiple variables.
*   **JSON Schema:**
    ```json
    {
      "type": "radar_chart",
      "title": "Évaluation Produit Multi-Critères",
      "config": { /* ... */ },
      "dimensions": [ /* ... */ ],
      "data": [
        {
          "series": "Produit A",
          "color": "#FF6B6B",
          "values": [85, 70, 90, 75, 80, 95]
        }
      ]
    }
    ```

### `treemap`

*   **Description:** A treemap for hierarchical data.
*   **JSON Schema:**
    ```json
    {
      "type": "treemap",
      "title": "Répartition du Chiffre d'Affaires",
      "config": { /* ... */ },
      "data": {
        "name": "CA Total",
        "children": [ /* ... */ ]
      }
    }
    ```

### `sankey_diagram`

*   **Description:** A Sankey diagram for showing flows.
*   **JSON Schema:**
    ```json
    {
      "type": "sankey_diagram",
      "title": "Flux de Revenus",
      "config": { /* ... */ },
      "data": {
        "nodes": [ /* ... */ ],
        "links": [ /* ... */ ]
      }
    }
    ```

### `timeline`

*   **Description:** A timeline for showing events over time.
*   **JSON Schema:**
    ```json
    {
      "type": "timeline",
      "title": "Roadmap Projet 2024",
      "config": { /* ... */ },
      "data": [ /* ... */ ],
      "milestones": [ /* ... */ ]
    }
    ```

### `box_plot`

*   **Description:** A box plot for showing data distribution.
*   **JSON Schema:**
    ```json
    {
      "type": "box_plot",
      "title": "Distribution des Salaires par Département",
      "config": { /* ... */ },
      "data": [
        {
          "category": "IT",
          "min": 35000,
          "q1": 42000,
          "median": 50000,
          "q3": 58000,
          "max": 75000,
          "outliers": [80000, 85000],
          "color": "#2196F3"
        }
      ]
    }
    ```

### `table`

*   **Description:** A data table with sorting, pagination, etc.
*   **JSON Schema:**
    ```json
    {
      "type": "table",
      "title": "Rapport Mensuel des Ventes",
      "config": { /* ... */ },
      "columns": [ /* ... */ ],
      "data": [ /* ... */ ]
    }
    ```

### `kpi_dashboard`

*   **Description:** A dashboard of Key Performance Indicators.

*   **JSON Schema:**
    ```json
    {
      "type": "kpi_dashboard",
      "title": "Dashboard Exécutif",
      "config": { /* ... */ },
      "kpis": [
        {
          "id": "revenue",
          "title": "Chiffre d'Affaires",
          "value": 2450000,
          "format": "currency",
          "change": 12.5,
          "change_type": "percentage",
          "period": "vs mois dernier",
          "color": "#4CAF50",
          "icon": "trending_up",
          "size": "large"
        }
      ]
    }
    ```

### `combo_chart`

*   **Description:** A combination of different chart types (e.g., bar and line).
*   **JSON Schema:**
    ```json
    {
      "type": "combo_chart",
      "title": "Ventes et Marge par Trimestre",
      "config": { /* ... */ },
      "axes": { /* ... */ },
      "series": [
        {
          "name": "Ventes",
          "type": "column",
          "axis": "y1",
          "color": "#2196F3",
          "data": [ /* ... */ ]
        },
        {
          "name": "Marge",
          "type": "line",
          "axis": "y2",
          "color": "#4CAF50",
          "data": [ /* ... */ ]
        }
      ]
    }
    ```

---

This documentation should provide a solid starting point for building a dynamic and responsive frontend that can render the rich visual outputs from the NeuralStark API.
