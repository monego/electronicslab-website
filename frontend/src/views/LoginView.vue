<template>
    <Navbar />
    <main class="flex justify-center items-center h-screen bg-[#fbfbfb]">
        <form>
            <div class="p-6 w-96 bg-white rounded shadow-sm">
                <div class="flex justify-center items-center mb-4">
                    <img src="https://nupedee.ufsm.br/s/css/logo.png" class="h-32" />
                </div>
                <div class="px-3 py-2 mb-3 text-gray-100 bg-red-500 rounded">
                    <p>Credenciais inválidas!</p>
                </div>
                <label class="text-gray-700">SIAPE</label>
                <input class="px-1 py-2 mb-4 w-full text-gray-500 bg-gray-200 outline-none" type="text" />
                <label class="text-gray-700">Senha</label>
                <input class="px-1 py-2 mb-4 w-full text-gray-500 bg-gray-200 outline-none" type="password" />
                <input class="mb-4" type="checkbox" />
                <label for="remember" class="pl-1 text-gray-700">Lembrar</label>
                <button type="submit"
                    class="py-2 w-full text-gray-100 bg-blue-600 rounded transition-colors hover:bg-blue-600">Login</button>
            </div>
        </form>
    </main>
</template>