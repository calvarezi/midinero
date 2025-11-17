import { Toaster } from "react-hot-toast";

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4500,
          style: {
            fontSize: "15px",
          }
        }}
      />

      <AppRouter />
    </>
  );
}
export default App;