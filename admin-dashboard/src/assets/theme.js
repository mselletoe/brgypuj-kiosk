// src/assets/blueTheme.js
export const blueThemeOverrides = {
  common: {
    primaryColor: '#0957FF',
    primaryColorHover: '#3C7EFF',
    primaryColorPressed: '#0043CC',
    borderRadius: '6px',
    textColorBase: '#373737',
    placeholderColor: '#999999'
  },
  Input: {
    color: '#FFFFFF',
    borderRadius: '6px',
    heightLarge: '42px',
    placeholderColor: '#999999',
    borderHover: '2px solid #8FB2FF',
    borderFocus: '2px solid #0957FF',
    boxShadow: '0 0 0 2px rgba(9, 87, 255, 0.3)'
  },
  Select: {
    peers: {
      InternalSelection: {
        color: '#FFFFFF',
        textColor: '#373737',
        borderRadius: '6px',
        heightLarge: '42px',
        placeholderColor: '#808080',
        borderHover: '2px solid #8FB2FF',
        borderFocus: '2px solid #0957FF',
        boxShadowFocus: '0 0 0 2px rgba(9, 87, 255, 0.3)'
      }
    }
  }
}