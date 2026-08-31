import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

type Geometry = {
  geometry_type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
};

export type ViewerComponent = {
  component_id: string;
  component_type: string;
  discipline: string;
  zone: string;
  geometry: Geometry;
};

  type EngineeringViewerProps = {
    highlightedIds: Set<string>;
    hasSearched: boolean;
    selectedComponentId: string | null;
    onSelectComponent: (
      component: ViewerComponent
    ) => void;
    onComponentsLoaded?: (
      components: ViewerComponent[]
    ) => void;

  zoom: number;
  viewerMode: "select" | "pan";
  resetViewSignal: number;
  fitViewSignal: number;
};


/* =========================================================
   ENGINEERING VIEWER
========================================================= */

export default function EngineeringViewer({
  highlightedIds,
  hasSearched,
  selectedComponentId,
  onSelectComponent,
  onComponentsLoaded,
  zoom,
  viewerMode,
  resetViewSignal,
  fitViewSignal,
}: EngineeringViewerProps) {

  const [components, setComponents] =
    useState<ViewerComponent[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [pan, setPan] = useState({
    x: 0,
    y: 0,
  });
  void resetViewSignal;
  void fitViewSignal;

  const [isDragging, setIsDragging] =
    useState(false);

  const dragStart = useRef({
    x: 0,
    y: 0,
  });


  /* =========================================================
     LOAD REAL MODEL
  ========================================================= */

  useEffect(() => {

    let cancelled = false;

    const loadComponents = async () => {

      try {

        setLoading(true);
        setError(null);

        const response = await fetch(
          "http://127.0.0.1:8000/api/viewer/components"
        );

        if (!response.ok) {
          throw new Error(
            `API returned ${response.status}`
          );
        }

        const data =
          await response.json();

        if (!cancelled) {

          const loadedComponents =
            data.components ?? [];

          setComponents(loadedComponents);

          onComponentsLoaded?.(loadedComponents);

        }

      } catch (err) {

        if (!cancelled) {

          setError(
            err instanceof Error
              ? err.message
              : "Unable to load engineering model."
          );

        }

      } finally {

        if (!cancelled) {
          setLoading(false);
        }

      }

    };

    loadComponents();

    return () => {
      cancelled = true;
    };

  }, [onComponentsLoaded]);


  /* =========================================================
     CALCULATE MODEL BOUNDS
  ========================================================= */

  const bounds = useMemo(() => {

    if (components.length === 0) {

      return {
        minX: 0,
        minY: 0,
        maxX: 1200,
        maxY: 900,
      };

    }

    let minX = Infinity;
    let minY = Infinity;

    let maxX = -Infinity;
    let maxY = -Infinity;


    for (const component of components) {

      const g =
        component.geometry;

      minX = Math.min(
        minX,
        g.x,
        g.x1
      );

      minY = Math.min(
        minY,
        g.y,
        g.y1
      );

      maxX = Math.max(
        maxX,
        g.x + g.width,
        g.x2
      );

      maxY = Math.max(
        maxY,
        g.y + g.height,
        g.y2
      );

    }


    return {
      minX,
      minY,
      maxX,
      maxY,
    };

  }, [components]);


  const padding = 40;

  const minX =
    bounds.minX - padding;

  const minY =
    bounds.minY - padding;

  const modelWidth =
    bounds.maxX -
    bounds.minX +
    padding * 2;

  const modelHeight =
    bounds.maxY -
    bounds.minY +
    padding * 2;


  const centerX =
    minX + modelWidth / 2;

  const centerY =
    minY + modelHeight / 2;


  const viewBox = [
    minX,
    minY,
    modelWidth,
    modelHeight,
  ].join(" ");



  /* =========================================================
     MOUSE PAN
  ========================================================= */

  const handleMouseDown = (
    event: React.MouseEvent<SVGSVGElement>
  ) => {

    if (viewerMode !== "pan") {
      return;
    }

    setIsDragging(true);

    dragStart.current = {
      x: event.clientX,
      y: event.clientY,
    };

  };


  const handleMouseMove = (
    event: React.MouseEvent<SVGSVGElement>
  ) => {

    if (
      !isDragging ||
      viewerMode !== "pan"
    ) {
      return;
    }

    const deltaX =
      event.clientX -
      dragStart.current.x;

    const deltaY =
      event.clientY -
      dragStart.current.y;


    /*
      Convert screen movement into
      model-space movement.
    */

    const scaleFactor =
      modelWidth /
      Math.max(
        event.currentTarget.clientWidth,
        1
      );


    setPan((previous) => ({
      x:
        previous.x +
        deltaX *
        scaleFactor /
        zoom,

      y:
        previous.y +
        deltaY *
        scaleFactor /
        zoom,
    }));


    dragStart.current = {
      x: event.clientX,
      y: event.clientY,
    };

  };


  const handleMouseUp = () => {
    setIsDragging(false);
  };


  const handleMouseLeave = () => {
    setIsDragging(false);
  };


  /* =========================================================
     LOADING
  ========================================================= */

  if (loading) {

    return (

      <div className="viewer-loading">

        <div className="viewer-loading-spinner" />

        <span>
          Loading engineering model...
        </span>

      </div>

    );

  }


  /* =========================================================
     ERROR
  ========================================================= */

  if (error) {

    return (

      <div className="viewer-error">

        <strong>
          Unable to load engineering model
        </strong>

        <span>
          {error}
        </span>

      </div>

    );

  }


  /* =========================================================
     RENDER
  ========================================================= */

  return (

    <svg
      className={`engineering-svg ${
        viewerMode === "pan"
          ? "pan-mode"
          : "select-mode"
      } ${
        isDragging
          ? "is-dragging"
          : ""
      }`}

      viewBox={viewBox}

      preserveAspectRatio="xMidYMid meet"

      role="img"

      aria-label="Engineering model"

      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
    >

      <g
        transform={`
          translate(
            ${centerX + pan.x}
            ${centerY + pan.y}
          )
          scale(${zoom})
          translate(
            ${-centerX}
            ${-centerY}
          )
        `}
      >

        {components.map(
          (component) => {

            const g =
              component.geometry;

            const highlighted =
              highlightedIds.has(
                component.component_id
              );

            const selected =
              selectedComponentId ===
              component.component_id;


            const classNames = [
              "viewer-component",

              `geometry-${g.geometry_type.toLowerCase()}`,

              hasSearched
                ? highlighted
                  ? "viewer-component-highlighted"
                  : "viewer-component-dimmed"
                : "",

              selected
                ? "viewer-component-selected"
                : "",

            ]
              .filter(Boolean)
              .join(" ");


            /* =================================================
               LINE
            ================================================= */

            if (
              g.geometry_type.toLowerCase() ===
              "line"
            ) {

              return (

                <line
                  key={
                    component.component_id
                  }

                  className={
                    classNames
                  }

                  x1={g.x1}
                  y1={g.y1}

                  x2={g.x2}
                  y2={g.y2}

                  strokeWidth={Math.max(
                    2,
                    Math.min(
                      8,
                      g.height || 3
                    )
                  )}

                  onClick={(event) => {

                    if (
                      viewerMode !==
                      "select"
                    ) {
                      return;
                    }

                    event.stopPropagation();

                    onSelectComponent(
                      component
                    );

                  }}

                />

              );

            }


            /* =================================================
               CIRCLE
            ================================================= */

            if (
              g.geometry_type.toLowerCase() ===
              "circle"
            ) {

              return (

                <ellipse
                  key={
                    component.component_id
                  }

                  className={
                    classNames
                  }

                  cx={
                    g.x +
                    g.width / 2
                  }

                  cy={
                    g.y +
                    g.height / 2
                  }

                  rx={
                    Math.max(
                      2,
                      g.width / 2
                    )
                  }

                  ry={
                    Math.max(
                      2,
                      g.height / 2
                    )
                  }

                  onClick={(event) => {

                    if (
                      viewerMode !==
                      "select"
                    ) {
                      return;
                    }

                    event.stopPropagation();

                    onSelectComponent(
                      component
                    );

                  }}

                />

              );

            }


            /* =================================================
               RECTANGLE / EQUIPMENT
            ================================================= */

            return (

              <rect
                key={
                  component.component_id
                }

                className={
                  classNames
                }

                x={g.x}
                y={g.y}

                width={Math.max(
                  g.width,
                  2
                )}

                height={Math.max(
                  g.height,
                  2
                )}

                rx={
                  g.geometry_type
                    .toLowerCase() ===
                  "tank"
                    ? Math.min(
                        g.width / 2,
                        12
                      )
                    : 2
                }

                transform={
                  g.rotation
                    ? `rotate(
                        ${g.rotation}
                        ${
                          g.x +
                          g.width / 2
                        }
                        ${
                          g.y +
                          g.height / 2
                        }
                      )`
                    : undefined
                }

                onClick={(event) => {

                  if (
                    viewerMode !==
                    "select"
                  ) {
                    return;
                  }

                  event.stopPropagation();

                  onSelectComponent(
                    component
                  );

                }}

              />

            );

          }
        )}

      </g>

    </svg>

  );

}