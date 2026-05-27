export const environment = {
  production: false,
  // Calls go through the API gateway (CORS enabled there).
  gatewayBase: 'http://localhost:8080',
  datalakeBase: 'http://localhost:8080/datalake',
};
