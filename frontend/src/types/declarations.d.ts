// Resmi @types paketi olmayan kütüphaneler için minimal beyanlar.
// Bu dosya yalnızca TS hatalarını giderir; runtime davranışını etkilemez.

declare module "react-leaflet-cluster" {
  import * as React from "react";
  import * as L from "leaflet";

  export interface MarkerClusterGroupProps {
    chunkedLoading?: boolean;
    showCoverageOnHover?: boolean;
    spiderfyOnMaxZoom?: boolean;
    maxClusterRadius?: number | ((zoom: number) => number);
    disableClusteringAtZoom?: number;
    children?: React.ReactNode;
    iconCreateFunction?: (cluster: L.MarkerCluster) => L.Icon | L.DivIcon;
    [key: string]: unknown;
  }

  const MarkerClusterGroup: React.FC<MarkerClusterGroupProps>;
  export default MarkerClusterGroup;
}

declare module "leaflet.heat" {
  // leaflet.heat global L objesine `heatLayer` ekler.
  // Bu side-effect import için boş modül yeterli.
}
