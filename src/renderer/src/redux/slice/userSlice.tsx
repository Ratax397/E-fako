import { createSlice, PayloadAction } from '@reduxjs/toolkit'


type  UserState ={
  name: string
}
// mila alagna reto @finition
const initialState:UserState = {
  name: '',
}

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<{ name: string }>) => {
      state.name = String(action.payload.name)
    }
  }
})

export const { setUser } = userSlice.actions
export default userSlice.reducer
