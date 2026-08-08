# Client-side surface (stock, narrated for the coverage census)

**Framing:** the stock game's client-side subsystems - reachable from the dedicated
boot + tick call graph (so they appear in the reached base) but executed on the
client. The authoritative classification stays in
[out-of-scope-surface.md](out-of-scope-surface.md); this doc narrates each type's role
(dump-derived base + key methods) so the whole reached surface reaches **100%
narrated** for the coverage census. No dedicated-server execution is implied.

## Coverage tiers

| Tier | Meaning |
|---|---|
| **narrated** | backticked in a hand-written narrative doc (this one, or a subsystem doc) |
| **classified** | listed only in out-of-scope-surface.md (not yet narrated here) |
| **unaccounted** | appears nowhere |

## Client UI (XUi / NGUI framework + bindings) (464)

The XUi / NGUI windowing framework: windows, widgets, bindings, and the data-binding expression engine that drive the in-game HUD and menus. Client-rendered; none of this executes on a dedicated server.

| Type | base | key methods |
|---|---|---|
| `BindingInfo` | Object | RefreshValue |
| `BindingInfoNcalc` | Object | RefreshValue, FindParameter, IsFullNcalcBinding |
| `BindingItem` | Object |  |
| `BindingItemCvar` | BindingItem | GetValue |
| `BindingItemNcalc` | BindingItem | FindParameter, evaluateExpression, GetValue |
| `BindingItemStandard` | BindingItem | GetValue |
| `BindingMethodCache` | Object | RegisterCustomBindingMethod, tryGetBindingObjectDelegate, getCacheForType |
| `BindingMethodData` | Object |  |
| `BindingMethodTypeCache` | Object | initCacheForController, TryGetBindingDelegate |
| `BindingNcalcFunctions` | Object | EvaluateFunc, format, serverinfoint |
| `BindingState` | Object | RefreshValue, ToString |
| `BindingsGroup` | Object | HasPref, Reset, get_VersionId |
| `BindingsManager` | Object | ReplaceCVars, CreateBinding, RefreshBindings |
| `CharAtlasData` | Object |  |
| `ChatMessagingHandler` | Object |  |
| `ChatTarget` | Object | CompareTo, IsValid, Send |
| `CommandModel` | Object |  |
| `ConsoleLine` | ValueType | GetLogColor |
| `ControllerGroup` | GameOptionsReset/EnumGamePrefGroup | Reset, get_VersionId |
| `ControllerLabelMapping` | ValueType |  |
| `GUIButtonPrompt` | MonoBehaviour | RefreshIcon, Awake, OnEnable |
| `GUIUtils` | Object | DrawArrow, segment_rect_intersection, RectIntersection |
| `GUIWindow` | Object | UiScaleMatrix, Equals, OnClose |
| `GUIWindowConsoleComponents` | MonoBehaviour | RefreshButtonPrompts, Awake |
| `GUIWindowNGUI` | GUIWindow | OnClose, OnOpen |
| `GUIWindowScreenshotText` | GUIWindow | OnGUI, writePlayerSkills, writePlayerBuffs |
| `GUIWindowUGUI` | GUIWindow | Update, OnOpen, OnClose |
| `UIAtlasFromFolder` | Object | createUiAtlasFromTextures, loadSpriteSettings, CreateUiAtlasFromFolder |
| `UIDisplayInfoFromXml` | Object | ParseItemDisplayInfo, ParseNode, ParseDisplayInfoEntry |
| `UIDisplayInfoManager` | Object | AddItemDisplayInfo, AddCharacterDisplayInfo, AddCraftingCategoryDisplayItem |
| `UIOptions` | Object | remove_OnOptionsVideoWindowChanged, add_OnOptionsVideoWindowChanged, set_OptionsVideoWindow |
| `UIUtils` | Object | GetButtonIconForAction, GetSpriteName, LoadAtlas |
| `XUiC_ActiveBuffEntry` | XUiC_SelectableEntry | GetBindingValueInternal, set_Notification, SelectedChanged |
| `XUiC_ActiveBuffList` | XUiController | Update, Init, OnOpen |
| `XUiC_AddWarpSettings` | XUiC_SignLayerSettings | Init, AddWarp, SetLayer |
| `XUiC_AdvancedColorPicker` | XUiController | Init, OnRGBAChanged, OnHexChanged |
| `XUiC_ArcWarpSettings` | XUiC_SignWarpSettings | Init, SetWarp, OnValueChangedGeneric |
| `XUiC_AssembleDroneWindow` | XUiC_AssembleWindow | GetBindingValueInternal, Init, BtnRepair_OnPress |
| `XUiC_AssembleWindow` | XUiController | GetBindingValueInternal, GetStatTitle, set_ItemStack |
| `XUiC_AssembleWindowGroup` | XUiController | OnOpen, set_ItemStack, OnClose |
| `XUiC_Backpack` | XUiC_ItemStackGrid | OnOpen, SetStacks, Update |
| `XUiC_BackpackWindow` | XUiController | GetBindingValueInternal, Init, UpdateLockedSlots |
| `XUiC_BagContainer` | XUiC_ItemStackGrid | GetBindingValueInternal, SetBag, Update |
| `XUiC_BasePartStack` | XUiC_SelectableEntry | GetBindingValueInternal, Update, HandleMoveToPreferredLocation |
| `XUiC_BindingEntry` | XUiController | set_Action, Update, newBindingClick |
| `XUiC_BlockedPlayersList` | XUiController | updateRecentList, updateBlockedList, OnOpen |
| `XUiC_BuffInfoWindow` | XUiC_InfoWindow | GetBindingValueInternal, set_Notification, Init |
| `XUiC_BuffPopoutList` | XUiController | Update, AddNotification, removeEntry |
| `XUiC_BugReportSaveSelect` | XUiController | rebuildList, Init, OnOpen |
| `XUiC_BugReportSavesList` | XUiC_List`1<XUiC_BugReportSavesList/ListEntry> | RebuildList, RebuildList |
| `XUiC_BugReportWindow` | XUiController | Update, handlePostSubmissionClose, OnOpen |
| `XUiC_BulgeWarpSettings` | XUiC_SignWarpSettings | Init, SetWarp, OnValueChangedGeneric |
| `XUiC_Button` | XUiController | onMouse, Update, Init |
| `XUiC_ButtonSelectable` | XUiC_Button | set_IsSelected, remove_OnButtonSelected, add_OnButtonSelected |
| `XUiC_CamPositionAdd` | XUiController | Init, OnVisibilityChanged, UpdateInput |
| `XUiC_CamPositionsList` | XUiC_List`1<XUiC_CamPositionsList/CamPerspectiveEntry> | RebuildList, Init, Add |
| `XUiC_CameraWindow` | XUiController | Update, OnClose, OnPreviewClicked |
| `XUiC_CaptionedTextBox` | XUiController | remove_OnSubmitHandler, remove_OnChangeHandler, add_OnSubmitHandler |
| `XUiC_CategoryEntry` | XUiController | ParseAttribute, XUiC_CategoryEntry_OnPress, GetBindingValueInternal |
| `XUiC_ChallengeEntry` | XUiController | GetBindingValueInternal, Update, OnHovered |
| `XUiC_ChallengeEntryDescriptionWindow` | XUiController | GetBindingValueInternal, RefreshButtonLabels, Update |
| `XUiC_ChallengeEntryList` | XUiController | Update, Init, OnPressEntry |
| `XUiC_ChallengeEntryListWindow` | XUiController | SetSelectedByUnlockData, OnOpen, Init |
| `XUiC_ChallengeGroupEntry` | XUiController | GetBindingValueInternal, Update, set_Entry |
| `XUiC_ChallengeGroupList` | XUiController | updateChallengeEntries, SetChallengeGroupEntryList, Init |
| `XUiC_ChallengeWindowGroup` | XUiController | OnOpen, Update, OnClose |
| `XUiC_CharacterCosmeticEntry` | XUiController | GetBindingValueInternal, ParseAttribute, Update |
| `XUiC_CharacterCosmeticList` | XUiController | SetCosmeticList, SetTempCosmeticSlot, UpdateCallouts |
| `XUiC_CharacterCosmeticWindow` | XUiController | OnOpen, Update, MakePreview |
| `XUiC_CharacterCosmeticWindowGroup` | XUiController | Init, OnOpen, Open |
| `XUiC_CharacterCosmeticsListWindow` | XUiController | BtnApplySet_OnPressed, GetBindingValueInternal, OnOpen |
| `XUiC_CharacterFrameWindow` | XUiController | GetBindingValueInternal, OnOpen, Update |
| `XUiC_CharacterSheetWindowGroup` | XUiController | OnOpen, OnClose, Init |
| `XUiC_ChatOutput` | XUiController | addMessage, ParseAttribute, AddMessage |
| `XUiC_CollectedItem` | XUiController | GetBindingValueInternal, Init, ShowItem |
| `XUiC_CollectedItemList` | XUiController | AddItemStack, RemoveItemStack, AddIconNotification |
| `XUiC_CollectorFuelWindow` | XUiController | GetBindingValueInternal, Update, Init |
| `XUiC_ColorPicker` | XUiController | Update, Init, setupSaturationVibranceTexture |
| `XUiC_CombineWindowGroup` | XUiController | OnOpen, Update, OnClose |
| `XUiC_ComboBoxBase` | XUiController | UpdateIndexMarkerPositions, Update, Init |
| `XUiC_ComboBoxBool` | Boolean> | UpdateLabel, set_Value, set_RelativeValue |
| `XUiC_ComboBoxFloat` | Double> | incrementalChangeValue, set_RelativeValue, get_RelativeValue |
| `XUiC_ComboBoxInt` | Int64> | incrementalChangeValue, set_RelativeValue, get_RelativeValue |
| `XUiC_CompanionEntry` | XUiController | GetBindingValueInternal, RefreshFill, Init |
| `XUiC_CompanionEntryList` | XUiController | RefreshPartyList, OnOpen, OnClose |
| `XUiC_ConfirmationPrompt` | XUiController | ShowPrompt, Update, Confirm |
| `XUiC_ContainerStandardControls` | XUiController | Init, MoveAll, MoveSmart |
| `XUiC_Counter` | XUiController | Init, TextInput_OnChangeHandler, Update |
| `XUiC_CraftingInfoWindow` | XUiC_InfoWindow | GetBindingValueInternal, Update, Init |
| `XUiC_CraftingListInfo` | XUiController | Init, Update, set_CategoryName |
| `XUiC_CraftingQueue` | XUiController | Update, RefreshQueue, AddRecipeToCraftAtIndex |
| `XUiC_Creative2Stack` | XUiC_ItemStack | SwapItem, setItemStack, HandleClickComplete |
| `XUiC_Creative2StackGrid` | XUiC_ItemStackGrid | Update, SetSlots, Init |
| `XUiC_Creative2WindowGroup` | XUiController | OnOpen, OnClose |
| `XUiC_Credits` | XUiController | loadCredits, OnOpen, getTemplates |
| `XUiC_CustomCharacterWindowGroup` | XUiController | BtnRandomize_OnPressed, setInitialOptions, cbxGenderOnValueChanged |
| `XUiC_DMPlayersList` | XUiC_DMBaseList`1<XUiC_DMPlayersList/ListEntry> | RebuildList, showProfileForEntry, Init |
| `XUiC_DMSavegamesList` | XUiC_DMBaseList`1<XUiC_DMSavegamesList/ListEntry> | RebuildList, FilterResults, SelectByName |
| `XUiC_DMWorldList` | XUiC_DMBaseList`1<XUiC_DMWorldList/ListEntry> | RebuildList, FilterResults, SelectByKey |
| `XUiC_DataManagementBar` | XUiController | refreshPreviewMode, refreshSelectionMode, refresh |
| `XUiC_DeathBar` | XUiController | GetBindingValueInternal, Update, Init |
| `XUiC_DemoWindow` | XUiController | GetBindingValueInternal, Init, OnOpen |
| `XUiC_DewCollectorContainer` | XUiC_VariableHeightGrid | SetSlots, SetItemInSlot, Init |
| `XUiC_DewCollectorModGrid` | XUiC_ItemStackGrid | SetTileEntity, TryAddMod, UpdateBackend |
| `XUiC_DewCollectorStack` | XUiC_RequiredItemStack | GetBindingValueInternal, Update, ParseAttribute |
| `XUiC_DewCollectorWindow` | XUiController | Update, GetBindingValueInternal, SetTileEntity |
| `XUiC_DewCollectorWindowGroup` | XUiController | SetTileEntity, Init, doEvent |
| `XUiC_DialogRespondentName` | XUiController | GetBindingValueInternal, set_CurrentDialog, Refresh |
| `XUiC_DialogResponseList` | XUiController | Update, Init, OnPressResponse |
| `XUiC_DialogStatementWindow` | XUiController | GetBindingValueInternal, Init, Update |
| `XUiC_DiscordBlockedUsers` | XUiController | Init |
| `XUiC_DiscordBlockedUsersList` | XUiC_List`1<XUiC_DiscordBlockedUsersList/Entry> | RebuildList, UpdateList, OnOpen |
| `XUiC_DiscordFriendsList` | XUiC_List`1<XUiC_DiscordFriendsList/FriendEntry> | RebuildList, GetBindingValueInternal, Init |
| `XUiC_DiscordInfo` | XUiController | btnSettings_OnPressed, closeAndOpenLoginWindow, closeAndOpenMainMenu |
| `XUiC_DiscordLobbyControl` | XUiController | GetBindingValueInternal, Init, ParseAttribute |
| `XUiC_DiscordLobbyMemberList` | XUiC_List`1<XUiC_DiscordLobbyMemberList/LobbyMember> | RebuildList, Init, Cleanup |
| `XUiC_DiscordMainMenuButton` | XUiController | GetBindingValueInternal, Update, Init |
| `XUiC_DiscordMainMenuFriends` | XUiController | OnOpen, GetBindingValueInternal, Update |
| `XUiC_DiscordPendingList` | XUiC_List`1<XUiC_DiscordPendingList/PendingEntry> | RebuildList, Init, Cleanup |
| `XUiC_DiscordVoiceControls` | XUiController | GetBindingValueInternal, Init, Update |
| `XUiC_DlcList` | XUiC_List`1<XUiC_DlcList/DlcEntry> | RebuildList, get_PagingRequired, OnOpen |
| `XUiC_DlcWindow` | XUiController | Update, updatePagingButtonIcons, OnOpen |
| `XUiC_DlcWindowNew` | XUiController | Update, updatePagingButtonIcons, OnOpen |
| `XUiC_DragAndDropWindow` | XUiController | set_CurrentStack, DropCurrentItem, ParseAttribute |
| `XUiC_DropDown` | XUiController | Init, UpdateFilteredList, updateCurrentPageContents |
| `XUiC_EditingTools` | XUiController | onWindowSelected, Init, Update |
| `XUiC_EditingToolsDialogBase` | XUiController | Update, OnOpen, OnClose |
| `XUiC_EditingToolsPoiEditor` | XUiC_EditingToolsDialogBase | Update, BtnStart_OnPressed, Init |
| `XUiC_EditorPanelSelector` | XUiController | OpenSelectedWindow, GetBindingValueInternal, OnClose |
| `XUiC_EditorStat` | XUiController | GetBindingValueInternal, Update, countBlockEntities |
| `XUiC_EmptyInfoWindow` | XUiC_InfoWindow | UpdateDescriptionText, Init, inputStyleChanged |
| `XUiC_EnteringArea` | XUiController | GetBindingValueInternal, Update, FadeUpdate |
| `XUiC_EquipmentStack` | XUiC_SelectableEntry | Update, ParseAttribute, OnHovered |
| `XUiC_EquipmentStackGrid` | XUiController | HandleSlotChangedEvent, SetStacks, OnClose |
| `XUiC_EulaWindow` | XUiController | formatPages, Update, loadDefaultXML |
| `XUiC_ExitingGame` | XUiController | OnOpen, Init |
| `XUiC_ExportPrefab` | XUiController | Init, TxtSaveNameOnOnChangeHandler, SaveAndClose |
| `XUiC_FocusedBlockHealth` | XUiController | SetData, GetBindingValueInternal, set_Text |
| `XUiC_FullScreenCollider` | XUiController | IsBlocked, visibilityChanged, Cleanup |
| `XUiC_GameEventMenu` | XUiController | OnOpen, Init, BtnSpawns_OnPress |
| `XUiC_GameEventsList` | XUiC_List`1<XUiC_GameEventsList/GameEventEntry> | RebuildList, OnOpen, set_Category |
| `XUiC_GamepadCalloutWindow` | XUiController | UpdateCalloutsForItemStack, GetCallout, Update |
| `XUiC_GridWarpSettings` | XUiC_SignWarpSettings | Init, SetWarp, OnValueChangedGeneric |
| `XUiC_HUDStatBar` | XUiController | GetBindingValueInternal, Update, setupActiveItemEntry |
| `XUiC_InGameDebugMenu` | XUiController | Init, BtnRecalcLight_Controller_OnPress, Update |
| `XUiC_InGameHUD` | XUiController | Update, Init |
| `XUiC_InGameMenuWindow` | XUiController | OnOpen, Init, GetBindingValueInternal |
| `XUiC_InGameTimeControls` | XUiController | Init, Update, btnTimeSkipBackPressed |
| `XUiC_InfoWindow` | XUiController | OnVisibilityChanged, Init, Cleanup |
| `XUiC_IngredientEntry` | XUiController | GetBindingValueInternal, Init, set_Ingredient |
| `XUiC_IngredientList` | XUiController | Update, Init, OnOpen |
| `XUiC_InteractionPrompt` | XUiController | SetText, GetBindingValueInternal, set_Text |
| `XUiC_ItemCosmeticStack` | XUiC_BasePartStack | CanSwap, SwapItem, GetPartName |
| `XUiC_ItemCosmeticStackGrid` | XUiController | HandleSlotChangedEvent, SetParts, OnOpen |
| `XUiC_ItemDronePartStack` | XUiC_ItemPartStack | CanRemove, CanSwap |
| `XUiC_ItemDronePartStackGrid` | XUiC_ItemPartStackGrid | Init, set_CurrentVehicle, get_CurrentVehicle |
| `XUiC_ItemInfoWindow` | XUiC_InfoWindow | GetBindingValueInternal, SetInfo, Update |
| `XUiC_ItemPartStack` | XUiC_BasePartStack | CanSwap, CanRemove, SwapItem |
| `XUiC_ItemPartStackGrid` | XUiController | SetParts, HandleSlotChangedEvent, OnOpen |
| `XUiC_ItemStack` | XUiC_SelectableEntry | HandleMoveToPreferredLocation, GetBindingValueInternal, Update |
| `XUiC_ItemStackGrid` | XUiController | SetStacks, FindFirstEmptySlot, AssembleLockSingleStack |
| `XUiC_ItemStackSlot` | XUiC_SelectableEntry | Update, itemTypeIcon, itemIcon |
| `XUiC_ItemStackSlotGrid` | XUiController | OnCellSelected, MoveToPreferred, SetSource |
| `XUiC_KaleidoWarpSettings` | XUiC_SignWarpSettings | Init, SetWarp, OnValueChangedGeneric |
| `XUiC_KeypadWindow` | XUiController | BtnOk_OnPressed, Init, OnClose |
| `XUiC_LevelTools3Window` | XUiController | Init, getRaycastHitPoint, Update |
| `XUiC_LevelToolsGenericWindow` | XUiController | initShapeMaterialReplacer, initBlockReplacer, initGenericButtons |
| `XUiC_LevelToolsHelpers` | Object | createSpecialAction, ReplaceBlockShapeMaterials, ReplaceBlockId |
| `XUiC_LightEditor` | XUiController | Init, Open, BtnPaste_OnPressed |
| `XUiC_ListEntry` | XUiController | set_Selected, Update, SetEntry |
| `XUiC_LoadingScreen` | XUiController | OnOpen, Update, cycle |
| `XUiC_Location` | XUiController | GetBindingValueInternal, Update, ParseAttribute |
| `XUiC_LoginBase` | XUiController | updateState, BtnRetry_OnPressed, BtnOffline_OnPressed |
| `XUiC_LootContainer` | XUiC_ItemStackGrid | SetSlots, OnClose, OnTileEntityChanged |
| `XUiC_LootWindow` | XUiController | GetBindingValueInternal, Update, SetTileEntityChest |
| `XUiC_LootWindowGroup` | XUiController | OpenLooting, openContainer, OnClose |
| `XUiC_MainMenuButtons` | XUiController | Init, CheckProfile, DoLoadSaveGameAutomation |
| `XUiC_MapEnterWaypoint` | XUiController | Init, Show, waypointOnSubmitHandler |
| `XUiC_MapInvitesList` | XUiController | UpdateInvitesList, onInviteAddToWaypoints, Init |
| `XUiC_MapInvitesListEntry` | XUiController | set_Selected, Init, Controller_OnPress |
| `XUiC_MapPopupEntry` | XUiController | OnHovered |
| `XUiC_MapPopupList` | XUiController | onPressEntry2, Init, onPressEntry1 |
| `XUiC_MapStats` | XUiController | GetBindingValueInternal, Update |
| `XUiC_MapSubPopupEntry` | XUiController | onPressed, SetSpriteName, select |
| `XUiC_MapSubPopupList` | XUiController | Init, ResetList |
| `XUiC_MapWaypoint` | XUiController | Init, HandleWaypointSetPressed |
| `XUiC_MapWaypointList` | XUiController | UpdateWaypointsList, Init, onWaypointRemovePressed |
| `XUiC_MapWaypointListEntry` | XUiController | Init, Controller_OnPress, updateSelected |
| `XUiC_MaterialInfoWindow` | XUiController | GetBindingValueInternal, SetMaterial, Update |
| `XUiC_MaterialStack` | XUiC_SelectableEntry | set_TextureData, Update, SetSelectedTextureForItem |
| `XUiC_MaterialStackGrid` | XUiController | SetMaterials, Update, Init |
| `XUiC_MaterialWindow` | XUiController | Init, FilterByName, OnOpen |
| `XUiC_MultiplayerPrivilegeNotification` | XUiController | resolvePrivilegesWithDialog, setContentVisibility, closeWindow |
| `XUiC_MultiplayerWindows` | XUiController | GetBindingValueInternal, UpdateInput, Update |
| `XUiC_NewContinueBase` | XUiC_PlayGameDialogBase | BtnStart_OnPressed, Init, updateBarUsageAndAllowanceValues |
| `XUiC_NewsScreen` | XUiController | Init, UpdateContinueLabel, UpdateInput |
| `XUiC_NewsWindow` | XUiController | Init, BtnLink_OnPressed, cycle |
| `XUiC_OptionEntryAbs` | XUiController | remove_ValueChanged, add_ValueChanged, set_OptionHovered |
| `XUiC_OptionEntryCustom` | XUiC_OptionEntryAbs | ResetToDefault, ApplySelection, DiscardCurrentChange |
| `XUiC_OptionEntryGamePrefAbs` | XUiC_OptionEntryComboAbs | parseGamePref, ApplySelection, Init |
| `XUiC_OptionEntryGamePrefBool` | XUiC_OptionEntryGamePrefAbs | set_SelectedValue, ResetToDefault, DiscardCurrentChange |
| `XUiC_OptionEntryGamePrefFloat` | XUiC_OptionEntryGamePrefAbs | set_SelectedValue, ResetToDefault, DiscardCurrentChange |
| `XUiC_OptionEntryGamePrefInt` | XUiC_OptionEntryGamePrefAbs | set_SelectedValue, ResetToDefault, DiscardCurrentChange |
| `XUiC_OptionEntryGamePrefIntIndex` | XUiC_OptionEntryGamePrefAbs | set_SelectedValue, initCurrentValue, Init |
| `XUiC_OptionEntryLegacy` | XUiC_OptionEntryAbs | get_IsDefault, get_IsChanged, initCurrentValue |
| `XUiC_OptionsBlockedPlayersList` | XUiC_OptionsDialogBase | OnClose, Init, get_SupportsDefaults |
| `XUiC_OptionsController` | XUiC_OptionsControlsBase | updateControllerMappingLabels, createControlsEntries, initControllerLayout |
| `XUiC_OptionsControls` | XUiC_OptionsControlsBase | createControlsEntries, Init, get_MouseSensitivityMin |
| `XUiC_OptionsControlsBase` | XUiC_OptionsDialogBase | storeCurrentBindings, doResetToDefaultsInternal, remove_OnSettingsChanged |
| `XUiC_OptionsControlsNewBinding` | XUiController | alreadyBound, onBindingReceived, OnOpen |
| `XUiC_OptionsGeneral` | XUiC_OptionsDialogBase | updateCrosshairElements, languageSavedOptions, initPermissionsBasedOptions |
| `XUiC_OptionsMenuNew` | XUiController | get_VideoOptionsSimplified, Update, Init |
| `XUiC_OptionsSelector` | XUiController | Init, Update, CycleRight |
| `XUiC_OptionsTwitch` | XUiC_OptionsDialogBase | OnOpen, updateOptions, Init |
| `XUiC_OptionsUsername` | XUiC_OptionsDialogBase | doSaveChangesInternal, OnOpen, Init |
| `XUiC_OptionsVideo` | XUiC_OptionsVideoBase | initQualityPresetBasedOptions, initResolutionOptions, OnQualityPresetChanged |
| `XUiC_OptionsVideoSimplified` | XUiC_OptionsVideoBase | initUpscalerModeOptions, initQualityPresetBasedOptions, remove_OnSettingsChanged |
| `XUiC_Paging` | XUiController | Init, updateControllerState, set_LastPageNumber |
| `XUiC_PartList` | XUiC_ItemStackGrid | SetSlots, SetAmmoSlot, SetSlot |
| `XUiC_PartyEntry` | XUiController | GetBindingValueInternal, Init, Update |
| `XUiC_PartyEntryList` | XUiController | RefreshPartyList, EntityPlayer_PartyJoined, OnOpen |
| `XUiC_PartyWindow` | XUiController | GetBindingValueInternal, Update, OnOpen |
| `XUiC_PerspectiveWarpSettings` | XUiC_SignWarpSettings | Init, SetWarp, OnValueChangedGeneric |
| `XUiC_PlayGameDialogBase` | XUiController | Update, OnOpen, OnClose |
| `XUiC_PlayGameMenu` | XUiController | onWindowSelected, OnOpen, get_OnlineMode |
| `XUiC_PlayerName` | XUiController | UpdatePlayerData, ShowProfile, CanShowProfile |
| `XUiC_PlayerProfile` | XUiC_PlayGameDialogBase | get_CanModifyProfile, BtnProfileDelete_OnPressed, get_UserProfileCount |
| `XUiC_PlayerProfileCreate` | XUiController | Update, BtnConfirmCreate_OnPressed, CreateProfileName_OnChangeHandler |
| `XUiC_PlayersBlockedListEntryBase` | XUiController | UpdateEntry, reportPlayerPressed, set_PlayerId |
| `XUiC_PlayersList` | XUiController | updatePlayersList, OnPlayerEventHandler, Init |
| `XUiC_PlayersListEntry` | XUiController | oniconPartyIconPress, Init, updatePartyStatus |
| `XUiC_PlayersRecentListEntry` | XUiC_PlayersBlockedListEntryBase | blockPlayerPressed, UpdateEntry, bntViewProfilePressed |
| `XUiC_PoiList` | XUiC_List`1<XUiC_PoiList/PoiListEntry> | RebuildList, OnOpen, set_FilterTier |
| `XUiC_PoiTeleportMenu` | XUiController | Init, EntryPressed, OnOpen |
| `XUiC_PopupMenu` | XUiController | Update, limitPositionToScreenBounds, clearItems |
| `XUiC_PopupMenuItem` | XUiController | SetEntry, onValueChanged, onPressed |
| `XUiC_PopupToolTip` | XUiController | DisplayTooltipText, Update, QueueTooltipInternal |
| `XUiC_PowerCameraWindowGroup` | XUiController | OnClose, Update, OnOpen |
| `XUiC_PowerRangedAmmoSlots` | XUiC_ItemStackGrid | Init, btnOn_OnPress, RefreshIsLocked |
| `XUiC_PowerRangedTrapOptions` | XUiController | SetupTargeting, Init, btnTargetZombies_OnPress |
| `XUiC_PowerRangedTrapWindowGroup` | XUiController | OnOpen, Update, Init |
| `XUiC_PowerSourceSlots` | XUiC_ItemStackGrid | SetRequirements, OnOpen, OnClose |
| `XUiC_PowerSourceStats` | XUiController | GetBindingValueInternal, btnOn_OnPress, BtnRefuel_OnPress |
| `XUiC_PowerSourceWindowGroup` | XUiController | OnOpen, Update, Init |
| `XUiC_PowerTriggerOptions` | XUiController | SetupSliders, Init, Update |
| `XUiC_PowerTriggerWindowGroup` | XUiController | Update, OnOpen, Init |
| `XUiC_PoweredGenericWindowGroup` | XUiController | Update, OnClose, set_TileEntity |
| `XUiC_PoweredSpotlightWindowGroup` | XUiC_PoweredGenericWindowGroup | OnOpen, Init, TileEntity_Destroyed |
| `XUiC_PrefabEditorHelp` | XUiController | Init, Close_OnPress |
| `XUiC_PrefabFeatureEditorList` | XUiC_List`1<XUiC_PrefabFeatureEditorList/FeatureEntry> | RebuildList, Init, OnAddFeaturePressed |
| `XUiC_PrefabFileList` | XUiC_List`1<XUiC_PrefabFileList/PrefabFileEntry> | RebuildList, SelectByLocation, SelectByName |
| `XUiC_PrefabFolderList` | XUiC_List`1<XUiC_PrefabFolderList/PrefabFolderEntry> | RebuildList, SelectByName, set_Mod |
| `XUiC_PrefabGroupsEditorList` | XUiC_PrefabFeatureEditorList | ToggleFeature, GetSupportedFeatures, FeatureEnabled |
| `XUiC_PrefabList` | XUiController | Init, BtnWorldPlacePrefabOnPressed, Update |
| `XUiC_PrefabPropertiesEditor` | XUiController | Init, TxtThemeRepeatDistance_OnChangeHandler, TxtDuplicateRepeatDistance_OnChangeHandler |
| `XUiC_PrefabQuestTags` | XUiC_PrefabFeatureEditorList | ToggleFeature, GetSupportedFeatures, FeatureEnabled |
| `XUiC_PrefabTagList` | XUiC_PrefabFeatureEditorList | ToggleFeature, FeatureEnabled, AddNewFeature |
| `XUiC_PrefabThemeTagList` | XUiC_PrefabFeatureEditorList | ToggleFeature, FeatureEnabled, AddNewFeature |
| `XUiC_PrefabTriggerEditorList` | XUiC_List`1<XUiC_PrefabTriggerEditorList/PrefabTriggerEntry> | RebuildList, OnOpen |
| `XUiC_PrefabZonesEditorList` | XUiC_PrefabFeatureEditorList | ToggleFeature, GetSupportedFeatures, FeatureEnabled |
| `XUiC_ProfilesList` | XUiC_List`1<XUiC_ProfilesList/ListEntry> | RebuildList, SelectByName, OnOpen |
| `XUiC_ProgressWindow` | XUiController | Update, Open, SetText |
| `XUiC_QuestDescriptionWindow` | XUiController | GetBindingValueInternal, set_CurrentQuest, SetQuest |
| `XUiC_QuestEntry` | XUiController | GetBindingValueInternal, ParseAttribute, set_Quest |
| `XUiC_QuestList` | XUiController | Update, set_SelectedEntry, Init |
| `XUiC_QuestListWindow` | XUiController | Init, ShowTrackButton, Update |
| `XUiC_QuestObjectiveEntry` | XUiController | GetBindingValueInternal, ParseAttribute, Update |
| `XUiC_QuestObjectiveList` | XUiController | Update, Init, SetIsTracker |
| `XUiC_QuestObjectivesWindow` | XUiController | GetBindingValueInternal, ParseAttribute, SetQuest |
| `XUiC_QuestRewardEntry` | XUiController | GetBindingValueInternal, get_QuestTypeKeyword, get_OptionalKeyword |
| `XUiC_QuestRewardList` | XUiController | Update, Init, set_Quest |
| `XUiC_QuestRewardsWindow` | XUiController | GetBindingValueInternal, set_CurrentQuest, SetQuest |
| `XUiC_QuestSharedEntry` | XUiController | GetBindingValueInternal, ParseAttribute, OnHovered |
| `XUiC_QuestSharedList` | XUiController | Update, Init, set_SelectedEntry |
| `XUiC_QuestSharedListWindow` | XUiController | ShowTrackButton, Init, showOnMapBtn_OnPress |
| `XUiC_QuestTurnInDetailsWindow` | XUiController | GetBindingValueInternal, set_CurrentQuest, OnOpen |
| `XUiC_QuestTurnInEntry` | XUiC_SelectableEntry | GetBindingValueInternal, OnHovered, Init |
| `XUiC_QuestTurnInRewardsWindow` | XUiController | GetBindingValueInternal, SetupOptions, BtnAccept_OnPress |
| `XUiC_QuestTurnInWindowGroup` | XUiController | OnOpen, OnClose, TryNextComplete |
| `XUiC_QuestWindowGroup` | XUiController | GetBindingValueInternal, OnOpen, Init |
| `XUiC_Radial` | XUiController | getBasicBlockInfo, SetupBlockShapeData, handleBlockShapeCommand |
| `XUiC_RadialEntry` | XUiController | Init, ParseAttribute, SetScale |
| `XUiC_RecipeCraftCount` | XUiC_Counter | calcMaxCraftable, OnOpen, GetBindingValueInternal |
| `XUiC_RecipeEntry` | XUiC_SelectableEntry | GetBindingValueInternal, Init, set_Recipe |
| `XUiC_RecipeList` | XUiController | Update, GetRecipeData, OnOpen |
| `XUiC_ReportPlayer` | XUiController | OnOpen, BtnSend_OnPressed, BtnKick_OnPressed |
| `XUiC_RequiredItemStack` | XUiC_ItemStack | TryStack, ItemAllowed, ParseItemClassesFromString |
| `XUiC_RwgBiome` | XUiController | set_BiomeIdx, remove_ValueChanged, add_ValueChanged |
| `XUiC_SDCSPreviewWindow` | XUiController | init, updateController, cameraVerticalPan |
| `XUiC_SaveDirtyPrefab` | XUiController | Show, GetBindingValueInternal, CloseWith |
| `XUiC_SaveIndicator` | XUiController | Update, Init, Cleanup |
| `XUiC_SaveManagementPrompt` | XUiController | updateDataBarPreview, validate, setValues |
| `XUiC_SavegamesList` | XUiC_List`1<XUiC_SavegamesList/ListEntry> | TrySelectEntry, SelectByName, RebuildList |
| `XUiC_SelectableEntry` | XUiController | set_IsSelected, get_IsSelected, SelectedChanged |
| `XUiC_ServerBrowserDirectConnect` | XUiController | TxtIp_OnClipboardHandler, Update, OnOpen |
| `XUiC_ServerBrowserGameOptionInputAdvanced` | XUiController | parse, Init, ControlText_OnChangeHandler |
| `XUiC_ServerBrowserGameOptionInputRange` | XUiController | GetFilter, Init, ControlText_OnChangeHandler |
| `XUiC_ServerBrowserGameOptionInputSimple` | XUiController | GetFilter, ComparisonLabel_OnPress, Init |
| `XUiC_ServerBrowserGamePrefInfo` | XUiController | SetCurrentValue, setupOptions, Init |
| `XUiC_ServerBrowserGamePrefSelector` | XUiController | setupOptions, GetFilter, SetCurrentValue |
| `XUiC_ServerBrowserGamePrefSelectorCombo` | XUiController | setupOptions, GetFilter, getValueRangeFilter |
| `XUiC_ServerBrowserGamePrefSelectorComboSandboxOption` | XUiC_ServerBrowserGamePrefSelectorCombo | setupOptions, set_SandboxOption, get_SandboxOption |
| `XUiC_ServerBrowserGamePrefString` | XUiController | GetFilter, Init, SetValue |
| `XUiC_ServerInfo` | XUiController | SetServerInfo, Init, get_SandboxPreset |
| `XUiC_ServerJoinRulesDialog` | XUiController | Init, Show, OnOpen |
| `XUiC_ServerPasswordWindow` | XUiController | Update, OpenPasswordWindow, BtnSubmit_OnPressed |
| `XUiC_ServersList` | XUiC_List`1<XUiC_ServersList/ListEntry> | updateSortType, SetServerTypeFilter, currentListUpdateThread |
| `XUiC_ServiceInfoWindow` | XUiC_InfoWindow | GetBindingValueInternal, SetInfo, Init |
| `XUiC_ShapeInfoWindow` | XUiController | GetBindingValueInternal, SetShape, GetStatTitle |
| `XUiC_ShapeMaterialInfoWindow` | XUiController | SetShape, GetBindingValueInternal, Init |
| `XUiC_ShapeStack` | XUiC_SelectableEntry | Update, GetBindingValueInternal, UpdateInput |
| `XUiC_ShapeStackGrid` | XUiController | SetShapes, Init, Update |
| `XUiC_SignColorSettings` | XUiC_SignLayerSettings | SetLayer, Init, OnValueChangedGeneric |
| `XUiC_SignDebugPanel` | XUiController | Init, Populate, SetAll |
| `XUiC_SignEditorControl` | XUiController | SetDefault, Init, set_defaultValue |
| `XUiC_SignGridEntry` | XUiC_SelectableEntry | Update, ParseAttribute, SelectedChanged |
| `XUiC_SignGroupSettings` | XUiC_SignLayerSettings | Init, BakeOffsetsRecursive, BakeColorRecursive |
| `XUiC_SignInfoWindow` | XUiController | Init, GetBindingValueInternal, SetSignInfo |
| `XUiC_SignInstanceWindow` | XUiController | SetupPreview, GetBindingValueInternal, InitialiseTo |
| `XUiC_SignLayer` | XUiC_SignGridEntry | GetBindingValueInternal, OnWillRender, Init |
| `XUiC_SignLayerDragAndDropIcon` | XUiController | Update, OnWillRender, Init |
| `XUiC_SignLayerGrid` | XUiController | HandleOnClick, UpdateLayers, Init |
| `XUiC_SignLayerSettings` | XUiController | SetDefaultValue |
| `XUiC_SignLayerType` | XUiC_SignGridEntry | ParseAttribute, GetBindingValueInternal, Init |
| `XUiC_SignNewLayerPanel` | XUiController | Init, LayerTypeText_OnBecameSelected, LayerTypePolygon_OnBecameSelected |
| `XUiC_SignNoiseSettings` | XUiC_SignLayerSettings | Init, SetLayer, OnValueChangedGeneric |
| `XUiC_SignPolygonSettings` | XUiC_SignLayerSettings | Init, SetLayer, OnValueChangedGeneric |
| `XUiC_SignStack` | XUiC_SelectableEntry | Update, set_SignId, ParseAttribute |
| `XUiC_SignStackGrid` | XUiController | SetSignIds, Init, Update |
| `XUiC_SignTextSettings` | XUiC_SignLayerSettings | SetLayer, Init, OnValueChangedGeneric |
| `XUiC_SignTransformSettings` | XUiC_SignLayerSettings | OnChangeHandler, Init, SetLayer |
| `XUiC_SignWarpSettings` | XUiC_SignLayerSettings | BtnRemove_OnPressed, Init, SetLayer |
| `XUiC_SimpleButton` | XUiController | Init, set_Enabled, remove_OnPressed |
| `XUiC_SizeBar` | XUiController | RefreshSelectionMode, Init, Refresh |
| `XUiC_SkewWarpSettings` | XUiC_SignWarpSettings | Init, SetWarp, OnValueChangedGeneric |
| `XUiC_SkillAttributeInfoWindow` | XUiC_InfoWindow | GetBindingValueInternal, Init, Update |
| `XUiC_SkillAttributeLevel` | XUiController | GetBindingValueInternal, btnBuy_OnPress, ParseAttribute |
| `XUiC_SkillBookInfoWindow` | XUiC_InfoWindow | GetBindingValueInternal, UpdateSkill, Init |
| `XUiC_SkillBookLevel` | XUiController | GetBindingValueInternal, ParseAttribute, get_CurrentSkill |
| `XUiC_SkillCraftingInfoEntry` | XUiController | GetBindingValueInternal, ParseAttribute, Update |
| `XUiC_SkillCraftingInfoWindow` | XUiC_InfoWindow | GetBindingValueInternal, UpdateSkill, Init |
| `XUiC_SkillEntry` | XUiController | GetBindingValueInternal, Update, GetGroupPointCost |
| `XUiC_SkillList` | XUiController | listSkills, updateFilteredList, Init |
| `XUiC_SkillListWindow` | XUiController | GetBindingValueInternal, Init, OnOpen |
| `XUiC_SkillPerkInfoWindow` | XUiC_InfoWindow | GetBindingValueInternal, Init, Update |
| `XUiC_SkillPerkLevel` | XUiController | GetBindingValueInternal, btnBuy_OnPress, ParseAttribute |
| `XUiC_SkillSkillInfoWindow` | XUiC_InfoWindow | GetBindingValueInternal, UpdateSkill, get_CurrentSkill |
| `XUiC_SkillSkillMilestone` | XUiController | GetBindingValueInternal, UpdateSkill, ParseAttribute |
| `XUiC_SkillWindowGroup` | XUiController | OnOpen, Update, Init |
| `XUiC_SlotPreview` | XUiController | OnOpen, OnClose, Init |
| `XUiC_SpawnBlockEditor` | XUiController | setBlock, Init, BtnOk_OnPressed |
| `XUiC_SpawnEntitiesList` | XUiC_List`1<XUiC_SpawnEntitiesList/SpawnEntityEntry> | RebuildList, OnOpen |
| `XUiC_SpawnMenu` | XUiController | Spawn, SpawnFiltered_OnPressed, Init |
| `XUiC_SpawnNearFriendsList` | XUiC_List`1<XUiC_SpawnNearFriendsList/ListEntry> | RebuildList, GetBindingValueInternal, OnOpen |
| `XUiC_StartPointEditor` | XUiController | GetBindingValueInternal, OnOpen, Init |
| `XUiC_StretchWarpSettings` | XUiC_SignWarpSettings | Init, SetWarp, OnValueChangedGeneric |
| `XUiC_SubtitlesDisplay` | XUiController | Update, DisplaySubtitle, setSubtitle |
| `XUiC_TabSelector` | XUiController | set_SelectedTabIndex, updateTabVisibility, Init |
| `XUiC_TabSelectorButton` | XUiController | Init, findClickableChild, set_Tab |
| `XUiC_TabSelectorTab` | XUiController | set_TabVisible, set_TabSelected, set_TabKey |
| `XUiC_TargetBar` | XUiController | GetBindingValueInternal, Update, ParseAttribute |
| `XUiC_TextInput` | XUiController | Init, Update, showVirtualKeyboard |
| `XUiC_ThrowPower` | XUiController | Status, GetBindingValueInternal, set_CurrentPower |
| `XUiC_TipWindow` | XUiController | ShowTip, GetBindingValueInternal, Init |
| `XUiC_ToggleButton` | XUiController | set_Enabled, Btn_OnPress, remove_OnValueChanged |
| `XUiC_ToolTip` | XUiController | Update, set_ToolTip, GetBindingValueInternal |
| `XUiC_Toolbelt` | XUiC_ItemStackGrid | Update, OnOpen, OnClose |
| `XUiC_ToolbeltWindow` | XUiController | GetBindingValueInternal, Update, Init |
| `XUiC_TraderItemEntry` | XUiC_SelectableEntry | GetBindingValueInternal, set_Item, OnHovered |
| `XUiC_TraderItemList` | XUiController | SetItems, set_SelectedEntry, Init |
| `XUiC_TraderWindowGroup` | XUiController | OnOpen, Update, Init |
| `XUiC_TwirlWarpSettings` | XUiC_SignWarpSettings | Init, SetWarp, OnValueChangedGeneric |
| `XUiC_TwitchActionEntry` | XUiController | GetBindingValueInternal, ParseAttribute, GetModifiedWithColor |
| `XUiC_TwitchActionEntryList` | XUiController | Update, Init, SetFirstEntry |
| `XUiC_TwitchActionHistoryEntry` | XUiController | GetBindingValueInternal, ParseAttribute, OnHovered |
| `XUiC_TwitchActionHistoryEntryList` | XUiController | Update, Init, SetFirstEntry |
| `XUiC_TwitchCommandEntry` | XUiController | GetBindingValueInternal, ParseAttribute, Update |
| `XUiC_TwitchCommandList` | XUiController | SetupCommandList, Update, ParseAttribute |
| `XUiC_TwitchEntryDescriptionWindow` | XUiController | GetBindingValueInternal, Init, Update |
| `XUiC_TwitchEntryListWindow` | XUiController | Update, GetBindingValueInternal, OnOpen |
| `XUiC_TwitchHowToWindow` | XUiController | GetBindingValueInternal, Init, Left_OnPress |
| `XUiC_TwitchInfoWindowGroup` | XUiController | OnOpen, Init, OnClose |
| `XUiC_TwitchLeaderboardEntry` | XUiController | ParseAttribute, GetBindingValueInternal, set_LeaderboardEntry |
| `XUiC_TwitchLeaderboardEntryList` | XUiController | Update, Init, SetFirstEntry |
| `XUiC_TwitchVoteEntry` | XUiController | GetBindingValueInternal, ParseAttribute, Update |
| `XUiC_TwitchVoteInfoEntry` | XUiController | GetBindingValueInternal, ParseAttribute, OnHovered |
| `XUiC_TwitchVoteInfoEntryList` | XUiController | Update, Init, SetFirstEntry |
| `XUiC_TwitchVoteList` | XUiController | Update, SetupWinner, SetupForVote |
| `XUiC_TwitchWindow` | XUiController | GetBindingValueInternal, Init, Update |
| `XUiC_TwitchWindowSelector` | XUiController | OpenSelectedWindow, openSelectorAndWindow, Init |
| `XUiC_UiLimitsWindow` | XUiController | calcArWidth, OnOpen, Update |
| `XUiC_UnlockByEntry` | XUiController | GetBindingValueInternal, Update, set_UnlockData |
| `XUiC_UnlockByList` | XUiController | Update, Init, set_Recipe |
| `XUiC_VariableHeightGrid` | XUiC_ItemStackGrid | Update, updateGridHeight, GetItemStackControllers |
| `XUiC_VehiclePartStackGrid` | XUiC_ItemPartStackGrid | set_CurrentVehicle, SetMods, get_CurrentVehicle |
| `XUiC_VehicleStats` | XUiController | GetBindingValueInternal, Init, OnOpen |
| `XUiC_VehicleWindowGroup` | XUiController | Update, set_CurrentVehicleEntity, OnClose |
| `XUiC_VideoPlayer` | XUiController | Update, PlayVideo, GetInstance |
| `XUiC_WindowNonPagingHeader` | XUiController | OnClose, OnOpen, Init |
| `XUiC_WindowSelector` | XUiController | openSelectorAndWindow, toggleCategory, tryCloseCurrentWindow |
| `XUiC_WoPropsPOIMarker` | XUiController | Init, updateValues, updatePartSpawnerSize |
| `XUiC_WoPropsSleeperVolume` | XUiController | Init, Update, getSelectedVolumeStats |
| `XUiC_WorkstationFuelGrid` | XUiC_WorkstationGrid | Update, hasAnyFuel, HasRequirement |
| `XUiC_WorkstationGrid` | XUiC_ItemStackGrid | AddToItemStackArray, TryStackItem, AddItem |
| `XUiC_WorkstationInputGrid` | XUiC_WorkstationGrid | DecItem, AddToItemStackArray, GetItemCount |
| `XUiC_WorkstationMaterialInputGrid` | XUiC_WorkstationInputGrid | SetWeight, Update, GetWeight |
| `XUiC_WorkstationMaterialInputWindow` | XUiController | HasRequirement, OnOpen, ParseAttribute |
| `XUiC_WorkstationOutputGrid` | XUiC_WorkstationGrid | UpdateBackend, OnOpen, OnClose |
| `XUiC_WorkstationOutputWindow` | XUiController | Update, Init |
| `XUiC_WorkstationToolGrid` | XUiC_WorkstationGrid | Init, TryAddTool, HasRequirement |
| `XUiC_WorkstationWindowGroup` | XUiC_CraftingWindowGroup | OnOpen, Update, syncTEfromUI |
| `XUiC_WorldEditor` | XUiC_EditingToolsDialogBase | BtnStart_OnPressed, Update, StartEditor |
| `XUiC_WorldEditorCreateWorld` | XUiController | BtnConfirm_OnPressed, Update, OnOpen |
| `XUiC_WorldGenerationWindowGroup` | XUiC_EditingToolsDialogBase | Init, close |
| `XUiC_WorldList` | XUiC_List`1<XUiC_WorldList/WorldListEntry> | RebuildList, FilterResults, SetUserDataStorageTypeFilter |
| `XUiC_WorldSelectionList` | XUiC_List`1<XUiC_WorldSelectionList/Entry> | RebuildList, OnOpen, OnClose |
| `XUiC_WorldSelectionPopup` | XUiController | Update, open, confirm |
| `XUiFromXml` | Object | IsMatchingPlatform, createView, parseWindowGroup |
| `XUiM_AssembleItem` | XUiModel | AddPartToItem, RefreshAssembleItem, SetPartCount |
| `XUiM_Dialog` | XUiModel |  |
| `XUiM_InGameService` | XUiModel | GetServiceStats, StringFormatHandler, StringFormatHandler |
| `XUiM_ItemStack` | XUiModel | GetStatItemValueTextWithCompareInfo, GetStatItemValueTextWithModInfo, GetStatItemValueTextWithModColoring |
| `XUiM_LootContainer` | XUiModel | StashItems, TakeAll, AddItem |
| `XUiM_Player` | XUiModel | GetStatValue, GetPlayer, GetFoodPercent |
| `XUiM_PlayerBuffs` | XUiModel | GetBuffDisplayInfo, GetCVarValueAsTimeString, ConvertToTimeString |
| `XUiM_PlayerEquipment` | XUiModel | EquipItem, IsWearing, GetStackFromSlot |
| `XUiM_Quest` | XUiModel | GetQuestRewards, GetChainQuestRewards, GetQuestItemRewards |
| `XUiM_Vehicle` | XUiModel | RepairVehicle, GetSpeedText, GetNoise |
| `XUiM_Workstation` | XUiModel | GetTotalBurnTimeLeft, GetBurnTimeLeft, SetToolInSlot |
| `XUiModel` | Object |  |
| `XUiSideSizes` | ValueType | TryParse, SetTop, SetRight |
| `XUiTweenAbs` | Object | parseCurve, get_SecondHalfLinear, ParseInitialAttributeValue |
| `XUiTweenAlpha` | XUiTweenAbs | AttributePlayToEnd, CreateTween, set_Start |
| `XUiTweenColor` | XUiTweenAbs | AttributePlayToEnd, CreateTween, set_Start |
| `XUiTweenFill` | XUiTweenAbs | AttributePlayToEnd, CreateTween, set_Start |
| `XUiTweenHeight` | XUiTweenAbs | AttributePlayToEnd, CreateTween, set_Start |
| `XUiTweenPosition` | XUiTweenAbs | AttributePlayToEnd, CreateTween, set_Start |
| `XUiTweenRotation` | XUiTweenAbs | AttributePlayToEnd, CreateTween, set_Start |
| `XUiTweenScale` | XUiTweenAbs | AttributePlayToEnd, CreateTween, set_Start |
| `XUiTweenWidth` | XUiTweenAbs | AttributePlayToEnd, CreateTween, set_Start |
| `XUiUpdater` | Object | Update, Add, Remove |
| `XUiUtils` | Object | ParseActionsMarkup, modifyAtlas, GetBindingXuiMarkupString |
| `XUiV_Button` | XUiV_ImageBased | updateData, updateCurrentSprite, set_Enabled |
| `XUiV_Empty` | XUiView | get_WorldCorners, get_UiRect |
| `XUiV_FilledSprite` | XUiV_Sprite | updateData, refreshBoxCollider, SetDefaults |
| `XUiV_GamepadIcon` | XUiV_Sprite | updateData, set_Button, InitView |
| `XUiV_Grid` | XUiView_WidgetBased | InitView, SetRepeatContentTemplateParams, OnGridSizeChanged |
| `XUiV_ImageBased` | XUiView_WidgetBased | opacityModColor, Update, set_GlobalOpacityModifier |
| `XUiV_Label` | XUiV_LabelBase | updateData, InitView, set_Text |
| `XUiV_LabelBase` | XUiView_WidgetBased | updateData, updateUrlTooltip, attributeSupportUrls |
| `XUiV_Panel` | XUiView | updateClipping, set_ClippingSoftness, set_ClippingSize |
| `XUiV_Rect` | XUiView_WidgetBased | refreshBoxCollider, InitView, captureComponents |
| `XUiV_ScrollBar` | XUiView | InitView, OnOpen, Connect |
| `XUiV_ScrollView` | XUiV_Panel | MakeVisible, controllerScroll, updateData |
| `XUiV_Sprite` | XUiV_ImageBased | updateData, applyAtlasAndSprite, set_Fill |
| `XUiV_Table` | XUiView | InitView, Update, OnOpen |
| `XUiV_TextList` | XUiV_LabelBase | updateData, AddLine, set_FirstLinePrefix |
| `XUiV_Texture` | XUiV_TextureBased | loadTexture, set_Path, UnloadTexture |
| `XUiV_TextureBased` | XUiV_ImageBased | updateData, CreateMaterial, UnloadTexture |
| `XUiV_Video` | XUiV_TextureBased | startVideo, updateRenderTexture, InitView |
| `XUiV_Window` | XUiView | setRootNode, Update, OnOpen |
| `XUiView` | Object | InitView, Update, OnHover |
| `XUiView_WidgetBased` | XUiView | refreshBoxCollider, anchorsParsed, InitView |
| `XUiWindowGroup` | GUIWindow | OnOpen, Init, OnClose |

## Infrastructure / utility / DTOs (366)

Generic infrastructure, collections, DTOs, and delegates used across the game (client and server sides). Reachable from the dedicated boot graph through shared helpers.

| Type | base | key methods |
|---|---|---|
| `AchievementCacheEntry` | ValueType |  |
| `ActionCategory` | Object |  |
| `ActionSetManager` | Object | LogActionSets, Remove, Pop |
| `ActionUserData` | Object | get_LocalizedDescription, get_LocalizedName |
| `ActivitySecret` | Object |  |
| `ArmorGroupInfo` | Object |  |
| `AssetBundleLoadTask` | LoadManager/LoadTask | get_IsDone, get_INTERNAL_IsPending, LoadSync |
| `AssetBundleManager` | Object | LoadAssetBundle, _get, GetAsync |
| `AssetBundleRef` | Object |  |
| `AssetBundleRequestTFP` | CustomYieldInstruction | get_keepWaiting, get_Asset, get_IsDone |
| `AssetBundles` | Object | Cleanup |
| `AssetMappings` | Object | ToDictionary, Add, get_Count |
| `AssetRefs` | Object | LogAssets, ReleaseAssets, AddAssetHandle |
| `AtlasManagerEntry` | Object |  |
| `AtomicCounter` | Object | Increment, Decrement, get_Value |
| `AtomicSafeHandleScope` | ValueType | Dispose |
| `AuthenticationValues` | Object |  |
| `AutoBindCache` | Object | getCache, get_Instance, BindEvents |
| `AutoBindTypeCache` | Object | BindEvents, BindComponents, initCacheForController |
| `BackedArrayHandleModeExtensions` | Object | CanWrite, CanRead |
| `BakeCollider` | Object |  |
| `BakeJob` | ValueType | End, Begin |
| `BaseAtlas` | Object |  |
| `BaseItemActionEntry` | Object | RefreshEnabled, set_SoundName, set_ShortCut |
| `BindComponentInfo` | Object | Bind, LogNoViewFound, bindParent |
| `BindEventInfo` | Object | Bind |
| `BitsUsedEvent` | Object | set_UserName, set_UserLogin, set_UserId |
| `BlendCycleTimer` | Object | Tick, FadeOut, Restart |
| `BlendTimer` | Object | Tick, BlendTo, BlendToRate |
| `BoundaryProjectorTreasure` | BoundaryProjector | set_WithinRadius, SetupProjectors, get_CurrentRadius |
| `Bounds2i` | ValueType | Encapsulate, ToBounds, Contains |
| `BundleTags` | Object | get_Tag |
| `CC` | Object | OnCollisionOverlap, UpdateVelocity, Move |
| `CachedMeshData` | Object | ApproximatelyEquals |
| `CallInfo` | Object | OnCallStatusChanged, UpdateMembers, OnParticipantChanged |
| `Callout` | MonoBehaviour | Awake, SetupCallout, RefreshIcon |
| `CamPositionsListEntryController` | XUiC_List`1/XUiC_ListEntry<XUiC_CamPositionsList/CamPerspectiveEntry> | Init, bindingDirection, bindingName |
| `ChangedAnimationParameters` | Object | Add, GetParameterLists, newPacket |
| `ChannelPointsRedemptionEvent` | Object | set_UserName, set_UserLogin, set_UserId |
| `CharSplitEnumerator` | ValueType | MoveToNextInternal, MoveNext, get_Current |
| `ColorOperation` | ValueType | EvaluateColor |
| `ColorSpectrum` | Object | GetValue, FromTexture, IsSupportedRawTextureFormat |
| `ColorSwatchApplicator` | MonoBehaviour | ApplySwatchToGameObject, ApplyColorSwatch, get_baseHairColorLoc |
| `ConfigModel` | Object |  |
| `ControlsGroup` | GameOptionsReset/EnumGamePrefGroup | Reset, get_VersionId, NeedsReset |
| `CoroutineCancellationToken` | Object | Cancel, IsCancelled |
| `CoroutineTask` | LoadManager/LoadTask | Update, Complete, get_IsDone |
| `CountPreset` | ValueType | ToString |
| `CreateCustomReward` | Object |  |
| `CursorControllerAbs` | MonoBehaviour | RefreshBounds, DebugDrawBound, InitCursorBounds |
| `DChunkSquareMeshPool` | Object | GetObject, get_Count, ReturnObject |
| `DMSUpdateConditions` | ValueType | SetBoolHolder, set_IsGameUnPaused, set_IsDMSInitialized |
| `DailyVoteEntry` | Object |  |
| `DataItemArrayRepairTools` | Object | set_Item, get_Item, get_Length |
| `DataLoader` | Object | ParseDataPathIdentifier, UnloadAsset, IsInResources |
| `DataPathIdentifier` | ValueType | get_IsBundle |
| `DefaultSignData` | Object | get_PolygonGroupLayers |
| `DictionaryExtension` | Object | CopyTo, ValuesEquals, CopyValuesTo |
| `DictionaryNameIdMapping` | Object | Add, FindId, Clear |
| `DiscordAudioDevice` | IPartyVoice/VoiceAudioDevice | ToString, get_Identifier |
| `DiscordBlockedUsersListEntryController` | XUiC_List`1/XUiC_ListEntry<XUiC_DiscordBlockedUsersList/Entry> | Init, SetEntry, bindingDisplayName |
| `DiscordFriendsListEntryController` | XUiC_List`1/XUiC_ListEntry<XUiC_DiscordFriendsList/FriendEntry> | bindingStatusText, bindingDiscordStateIcon, Init |
| `DiscordInviteListener` | Object | TakePendingInvite, ConnectToInvite, get_ListenerInstance |
| `DiscordPendingListEntryController` | XUiC_List`1/XUiC_ListEntry<XUiC_DiscordPendingList/PendingEntry> | Init, SetEntry, bindingDisplayName |
| `DiscordSettings` | Object | OnGamePrefChanged, Load, remove_VoiceVadThresholdChanged |
| `DiscordUser` | Object | logPresenceInfo, SendFriendRequest, AcceptInvite |
| `DiscordUserMappingManager` | Object | SendMappingsToClient, GetAll, UpdateMapping |
| `DiscordUserSettingsManager` | Object | Load, Save, SetUserVolume |
| `DismembermentAccessoryMan` | MonoBehaviour | HidePart |
| `DisplayData` | Object | HandleCheckCrafting, GetUnlockItemRecipes, HandleCheckEnabled |
| `DisplayInfoEntry` | Object | set_Tags, get_Tags |
| `DlcListEntryController` | XUiC_List`1/XUiC_ListEntry<XUiC_DlcList/DlcEntry> | Init, OnHovered, bindingTextureUri |
| `DropSource` | Object | RequestData, ApplyBytes, GetData |
| `DropSourceRfs` | TwitchDropAvailabilityManager/DropSource | GetDataCo |
| `DropSourceWww` | TwitchDropAvailabilityManager/DropSource | GetDataCo |
| `DummyHandle` | Object | Copy, Release |
| `DummyScope` | Object | Dispose |
| `EModelNpc` | EModelBase | Init, createAvatarController, setupColliders |
| `EModelPlayer` | EModelBase | SetSkinTexture |
| `EModelStandard` | EModelBase | PostInit |
| `EModelSupplyCrate` | EModelBase | SetSkinTexture, Init |
| `EffectDisplayValue` | Object | GetValue, ParseDisplayValue, InLevelRange |
| `EffectGroupDescription` | Object | ParseDescription, get_Description, get_LongDescription |
| `EntryComparer` | Object | Compare |
| `EntryController` | XUiC_List`1/XUiC_ListEntry<XUiC_SpawnersList/SpawnerEntry> | bindingName |
| `EntryController` | XUiC_List`1/XUiC_ListEntry<XUiC_SpawnersList/SpawnerEntry> | bindingName |
| `EntryController` | XUiC_List`1/XUiC_ListEntry<XUiC_SpawnersList/SpawnerEntry> | bindingName |
| `EnumerableDebugWrapper` | DebugWrapper | GetEnumerator |
| `EosAudioDevice` | IPartyVoice/VoiceAudioDevice | LogDevice, ToString, get_Identifier |
| `EosConnectionTestInfo` | Object |  |
| `EventSubClient` | Object | HandleMessage, Disconnect, Reconnect |
| `EventSubMessage` | Object | set_Payload, set_Metadata, get_Payload |
| `EventSubMetadata` | Object | set_MessageType, set_MessageTimestamp, set_MessageId |
| `FastWireNode` | MonoBehaviour | BuildMesh, Awake, TogglePulse |
| `FavoritesHistoryKey` | Object | Equals, Equals, FromString |
| `FavoritesHistoryValue` | Object | FromString, ToString |
| `Field` | Object |  |
| `FileBackedArrayHandle` | Object | Dispose, OnWritten, FlushInternal |
| `FileBackedArrayMemoryManager` | MemoryManager`1<T> | Pin, Dispose, GetSpan |
| `FileLoadTask` | LoadManager/LoadTask | LoadSync, CompleteNow, Complete |
| `FirstPersonAnimator` | BodyAnimator | SetDrunk |
| `FloatRange` | ValueType | ToString, IsSet, Random |
| `FriendEntry` | XUiListEntry`1<XUiC_DiscordFriendsList/FriendEntry> | CompareTo, getUserSectionType, MatchesSearch |
| `FriendsServerList` | Object | OnServerFound, Init, StartSearch |
| `GSRequestData` | Object | GetInt, GetFloat, GetGSData |
| `GameOptionValue` | ValueType | Equals, GetHashCode, Equals |
| `GameOptionValue` | ValueType | Equals, GetHashCode, Equals |
| `GameOptionValue` | ValueType | Equals, GetHashCode, Equals |
| `GameOptionValue` | ValueType | Equals, GetHashCode, Equals |
| `GameOptionsControls` | Object | Load, Export, Save |
| `GameOptionsPlatforms` | Object | CalcDefaultGfxPreset, FindGfxName, GetItemIconFilterString |
| `GameOptionsReset` | Object | ResetGame, Init, GetGroupId |
| `GameWorldInfo` | ValueType | ToString, get_IsRandomWorld |
| `Gear` | Object |  |
| `GearBoneMap` | MonoBehaviour | Bake, SetBones, GetPartBones |
| `GearVariantMatrixSO` | ScriptableObject | EnsureIndex, TryParsePart, TryGetVariant |
| `GenderKey` | ValueType |  |
| `GenerateVoxelCubeSurface` | Object | GenerateYZ, GenerateXZ, GenerateXY |
| `GeometryUtils` | Object | RotateRectAboutY, IntersectRayTriangle, NearestPointOnEdgeLoop |
| `GlobalAssets` | Object | FindShader, LoadShaderMappings |
| `GlobalCultureInfo` | Object | SetDefaultCulture |
| `GoalData` | Object | set_goal, get_goal |
| `GroundWaterBounds` | ValueType | get_IsGroundWater |
| `HSBColor` | ValueType | ToColor, FromColor, Lerp |
| `HSVUtil` | Object | ConvertHsvToRgb, ConvertRgbToHsv, ConvertRgbToHsv |
| `HairColorSwatch` | ScriptableObject | ApplySwatchToGameObject, ApplyToMaterial |
| `HistoryState` | Object | SetSnapshotData, SetSnapshotData, InitPending |
| `HistoryStateManager` | Object | ProcessPendingChange, LogUndoRedoStack, ApplyHistoryState |
| `HotZoneSettings` | Object |  |
| `HsvColor` | ValueType | ToString, set_normalizedH, get_normalizedH |
| `HypeTrainProgressEvent` | Object | set_Level, get_Level |
| `IKController` | MonoBehaviour | ModifyRig, OnAnimatorIK, Start |
| `ILaunchPrefExtensions` | Object | CreateCommandLineArgument, ToCommandLine, ToCommandLine |
| `ImposterCanvas` | Object | Read, Write, Clone |
| `InControlExtensions` | Object | GetBindingString, GetKeyboardSourceString, GetBoundAction |
| `InGameService` | Object | set_ServiceType, set_Price, set_Name |
| `InputUtils` | Object | EnableAllPlayerActions, get_ControlKeyPressed, get_IsMac |
| `IntHashMapEntry` | Object | equals, toString, hashCode |
| `IntVect` | ValueType | Equals, op_Equality, GetHashCode |
| `JobBatch` | Object | TryApplyAndDispose, Dispose, Start |
| `JobState` | Object | Dispose, Start, CopyToMeshData |
| `KeyCollection` | ValueType | CopyTo, GetEnumerator, Remove |
| `KeysView` | Object | GetEnumerator, get_Count |
| `LabelUrlUtils` | Object | tryGetDataForLabelPos, BuildUrlFunctionString, handleChatTargetUrlHover |
| `LanguageInfo` | ValueType | CompareTo, ToString, Equals |
| `LayerStackInfo` | ValueType |  |
| `LevelRequirement` | ValueType |  |
| `ListEntry` | Object | SetBlockState, Write, Read |
| `ListEntry` | Object | SetBlockState, Write, Read |
| `ListEntry` | Object | SetBlockState, Write, Read |
| `ListEntry` | Object | SetBlockState, Write, Read |
| `ListEntry` | Object | SetBlockState, Write, Read |
| `ListEntry` | Object | SetBlockState, Write, Read |
| `LiteNetLibAuthWrapperClient` | Object | OnNetworkReceiveEvent, OnPeerConnectedEvent, OnPeerDisconnectedEvent |
| `LiteNetLibAuthWrapperServer` | Object | OnNetworkReceiveEvent, Update, ConnectionRequestCheck |
| `LoadGroup` | Object | IncrementPending, DecrementPending, get_Pending |
| `LoadSaveGame` | Object | GetState, AdvanceStateFrom, SetFailed |
| `Lobby` | Object | RemoveClient, AddClient, get_IsEmpty |
| `LobbyInfo` | Object | Join, UpdateMembers, Leave |
| `LocalPlayerCamera` | MonoBehaviour | OnPreCull, ModifyCameraProperties, Init |
| `LocalPlayerManager` | Object | HandleLocalPlayerChanged, remove_OnLocalPlayersChanged, add_OnLocalPlayersChanged |
| `LocationSlotInfo` | ValueType |  |
| `ManualTaskScheduler` | TaskScheduler | ProcessTasks, GetScheduledTasks, TryDequeue |
| `MapRenderBlockBuffer` | Object | SetPartNative, ScaleNative, LoadBlock |
| `MapRenderer` | Object | RenderFullMap, RenderDirtyChunks, getWorldExtent |
| `MapTileCache` | AbstractCache | GetFileContent, LoadTile, SaveTile |
| `MemoryBackedArrayHandle` | Object | get_Mode, Flush, Dispose |
| `MemoryBackedArrayUnsafeHandle` | Object | Dispose, ThrowIfCannotWrite, Finalize |
| `MemoryBackedArrayView` | Object | Dispose, ThrowIfCannotWrite, Finalize |
| `MessageButton` | XUiController | Update, Set, Clear |
| `MicroSplatProceduralTextureConfig` | ScriptableObject | GetCurveTexture, GetParamTexture, GetSlopeHSVTexture |
| `MicroSplatPropData` | ScriptableObject | RevisionData, GetTexture, GetGlobalSlopeFilter |
| `Morphable` | MonoBehaviour | MorphHeadgear |
| `MovementInput` | Object | Equals, Copy, Clear |
| `MultiSourceAtlasManager` | MonoBehaviour | CleanupAfterGame, recalcSpriteSources, GetAtlasForSprite |
| `MySimpleMesh` | Object | GetHashCode |
| `NGuiAction` | Object | OnSelect, SetTooltip, OnRelease |
| `NameData` | ValueType | ToString |
| `NativeDefault` | Object | AppendLastValue, Cleanup, set_Header |
| `NavObjectSettings` | Object | Init |
| `NewsEntry` | Object | FromXml, GetHashCode, Equals |
| `NewsSource` | Object | LoadXml, RequestData, GetData |
| `NewsSourceRfs` | NewsManager/NewsSource | startNextImageRequest, imageRequestCompleted, RequestImage |
| `NewsSourceWww` | NewsManager/NewsSource | requestFromUri, RequestImage, GetDataCo |
| `Occludee` | MonoBehaviour | OnEnable, Refresh, OnDisable |
| `OccludeeEntity` | Object |  |
| `OccludeeLayer` | Object | AddTransform |
| `OccludeeRenderers` | Object |  |
| `OccludeeZone` | Object | AddTransform, RemoveTransform, GetIndex |
| `OnCountChangedEventArgs` | EventArgs | set_Count, get_Count |
| `OnScreenIcon` | Object | Update, CreateObjects, SetupSubSprite |
| `ParsingMethodTypeCache` | Object | initCacheForController, TryGetParsingDelegate |
| `Perspective` | Object | FromXml, ToXml, ToPlayer |
| `PhysicsBodyNullCollider` | PhysicsBodyColliderBase | set_ColliderMode |
| `PhysicsBodySphereCollider` | PhysicsBodyColliderBase | set_ColliderMode |
| `PinnedBuffer` | Object | Create |
| `PlatformUserBlockedData` | Object | RefreshBlockedState, ToString, set_Locally |
| `PlatformUserBlockedResults` | Object | ToString, Block, set_HasErrored |
| `PlatformUserData` | Object | set_NativeId, ToString, MarkBlockedStateChanged |
| `PlatformUserDetailsResult` | Object |  |
| `PlayAndCleanup` | Object | StopWhenDone, StopBeginWhenDone |
| `PlayerActionsBase` | PlayerActionSet | AsyncResetControllerBindings, InitActionSet, set_Name |
| `PlayerActionsGUI` | PlayerActionsBase | CreateActions, CreateDefaultJoystickBindings, CreateDefaultKeyboardBindings |
| `PlayerActionsGlobal` | PlayerActionsBase | CreateActions, CreateDefaultKeyboardBindings, Init |
| `PlayerActionsLocal` | PlayerActionsBase | CreateActions, CreateDefaultKeyboardBindings, ConfigureJoystickLayout |
| `PlayerActionsPermanent` | PlayerActionsBase | CreateActions, CreateDefaultKeyboardBindings, CreateDefaultJoystickBindings |
| `PlayerActionsVehicle` | PlayerActionsBase | CreateActions, CreateDefaultJoystickBindings, CreateDefaultKeyboardBindings |
| `PlayerReportCategory` | Object |  |
| `PlayerReportCategoryEos` | IPlayerReporting/PlayerReportCategory | ToString |
| `PoiSizeInfo` | Object | ToString, get_Size |
| `Pool` | Object | DestroyTexturesAndClear, TryUnpool, TryRemove |
| `PoolItem` | Object | Instantiate |
| `Pref` | Object | TryParse, TryToString, TryGet |
| `PrefVersionStore` | Object | TryGetGamePref, Apply, Save |
| `PresenceManager` | Object | setDetailsAndState, setSmallImageAndTooltip, setLargeImageAndTooltip |
| `ProfileSDF` | Object | CreateTempArchetype, removeProfileName, SaveProfile |
| `ProfilingMetricCapture` | Object | PrettyPrint, GetCsvHeader, GetLastValueCsv |
| `PropEntityData` | Object |  |
| `PropTransform` | ValueType | Equals, Read, Write |
| `PubSubListenData` | Object | set_topics, set_auth_token, get_topics |
| `QualityInfo` | Object | HexToRGB, GetQualityLevelName, HexToInt |
| `RaidEvent` | Object | set_viewerCount, set_RaiderUserName, set_RaiderID |
| `ReadRequestDetails` | Object |  |
| `ReadScope` | ValueType | Dispose |
| `ReadScope` | ValueType | Dispose |
| `ReadWriteScope` | Object | Dispose, Finalize, Dispose |
| `ReaderWriterLockSlimExtensions` | Object | WriteLockScope, UpgradableReadLockScope, ReadLockScope |
| `Receiver` | Object | get_ModName |
| `ReflectionManager` | Object | FrameUpdate, ApplyProbeOptions, ApplyProbeOptions |
| `RegularCellData` | Object | GetVertexCount, GetTriangleCount |
| `RegularVertexData` | Object | get_Item |
| `ReleaseAssetsOnDestroy` | MonoBehaviour | CopyTo, OnDestroy, AddAssetHandle |
| `RenderTextureSystem` | Object | Create, SetTarget, SetTargetNoCopy |
| `RequestDetails` | Object | remove_Callback, add_Callback, ExecuteCallback |
| `ResolutionInfo` | ValueType | DimensionsToAspectRatio, CompareTo, Equals |
| `RootTransformRefParent` | RootTransformRef | FindRoot, FindTopTransform, Awake |
| `Row` | Object |  |
| `RtOwner` | ValueType |  |
| `RuntimeRenderingInfo` | ValueType |  |
| `SDCSArchetypesFromXml` | Object | parseArchetype, Save, parseEquipment |
| `SDCSDataUtils` | Object | Load, Save, ParseRaceVariantFromResources |
| `SDCSUtils` | Object | setupEquipment, Stitch, setupHairObjects |
| `SHandlerData` | ValueType |  |
| `SMainMenuOpenedData` | ValueType |  |
| `SMainMenuOpeningData` | ValueType |  |
| `SPosRot` | ValueType | Write, Read |
| `ScoreDisplay` | Object | Update, RemoveNavObject, Cleanup |
| `ScriptMethods` | Object | GetMethods |
| `SdXmlDocumentExtensions` | Object | SdSave, SdLoad |
| `SdfBinary` | SdfTag | WritePayload |
| `SdfBool` | SdfTag | WritePayload |
| `SdfByteArray` | SdfTag | WritePayload |
| `SdfFloat` | SdfTag | WritePayload |
| `SdfInt` | SdfTag | WritePayload |
| `SdfString` | SdfTag | WritePayload |
| `SendException` | Exception |  |
| `SendInfo` | ValueType |  |
| `SendInfo` | ValueType |  |
| `Server` | Object | Play, Play, EntityAddedToWorld |
| `Server` | Object | Play, Play, EntityAddedToWorld |
| `ServerFilter` | Object |  |
| `ServerKey` | ValueType | Equals, GetHashCode |
| `SessionModificationCallbackArgs` | Object |  |
| `SessionSearchArgs` | Object |  |
| `SexGearTables` | Object | ApplyUnifiedReorder, EnsureShapes, GetTable |
| `ShapeData` | Object | Clone |
| `ShapeSettings` | Object | Equals, CopyFrom, ResetToDefault |
| `SharedMaterialGroup` | Object | Update, RegisterActiveRenderer, DeregisterActiveRenderer |
| `ShrinkThreshold` | ValueType | ToString |
| `SignFontData` | Object | ConstructAtlasDataMap, TryGetCharAtlasData, set_LineHeight |
| `SignRenderingData` | Object | DisposeBuffers, Reset, Dispose |
| `SimpleMeshDataArray` | Object | ReadFromReader, ToMeshes, Dispose |
| `SimpleMeshDataWrapper` | ValueType | set_Name, get_Name, get_MeshData |
| `SimpleMeshFile` | Object | writeMesh, WriteGameObject, readData |
| `SimpleMeshInfo` | Object |  |
| `SingleThreadTaskScheduler` | TaskScheduler | Dispose, TaskThread, QueueTask |
| `SizeUtils` | Object | FormatSize, FormatSize, FormatSize |
| `SlotAllowedBonesCache` | Object | TryGet, Set, Remove |
| `SlotData` | Object |  |
| `SpanUtils` | Object | GetHashCodeInternal, Concat, Concat |
| `StackPanel` | Object |  |
| `StackSortUtil` | Object | CombineAndSortStacks, SortStacks, getGroup |
| `StatCacheEntry` | ValueType |  |
| `StatEntry` | Object |  |
| `StepSound` | Object | FromString |
| `StorageOperation` | ValueType |  |
| `StringSpan` | ValueType | Trim, Equals, CompareTo |
| `StringTable2D` | Object | EnsureShapeSymmetric, ApplyReorder, ClampValuesToValidOptions |
| `StringUtils` | Object | OnLanguageSelected, ToUpperWithUserLocale, ToLowerWithUserLocale |
| `StyleData` | Object |  |
| `StyleEntryData` | Object | get_Value |
| `Submission` | Object | get_Enabled |
| `SubscriptionEvent` | SubscriptionEventBase | set_IsGift, get_IsGift |
| `SubscriptionEventBase` | Object | set_UserName, set_UserLogin, set_UserId |
| `SubscriptionGiftEvent` | SubscriptionEventBase | set_Total, set_IsAnonymous, get_Total |
| `SubscriptionMessageEvent` | SubscriptionEventBase | set_StreakMonths, set_DurationMonths, set_CumulativeMonths |
| `TGALoader` | Object | LoadTGA, LoadTGAAsArray, loadPart |
| `TabChangeHelper` | Object | hasAnyUnsavedChange, hasAnyNonDefault, UpdateTab |
| `Tables` | Object |  |
| `TaskInfo` | Object | WaitForEnd |
| `TemporaryObject` | MonoBehaviour | SetLife, LogTO, Restart |
| `TextEllipsisAnimator` | Object | SetBaseString, UpdateLabel, GetNextAnimatedString |
| `ThreadContainer` | Object | Clear, Init, ThreadExtraWork |
| `ThreadContainerPool` | Object | GetObject, ReturnObject, get_Count |
| `ThreadData` | Object |  |
| `ThreadData` | Object |  |
| `ThreadSafeSemantics` | Object | Synchronize, Synchronize, InterlockedAdd |
| `TileAreaUtils` | Object | MakeKey, GetTileXPos, GetTileZPos |
| `TimerEventData` | Object | remove_FullTimeFinishEvent, remove_CloseEvent, remove_AlternateEvent |
| `TitleStorageOverridesManager` | Object | FetchFromSource, GetLocalPlatformNetworkString, remove_fetchFinished |
| `ToggleCapsLock` | MonoBehaviour | GetScrollLock |
| `Tooltip` | Object | Equals, Equals, GetHashCode |
| `TotalTrackedPS5` | Object | AppendLastValue, Cleanup, set_Header |
| `TransformCatalog` | Transform> | AddRecursive |
| `TransformLevel` | ValueType |  |
| `TriggerEffectDualsensePC` | Object | ApplyEffectDualsenseOnPC, SetWeaponEffect, SetTriggerEffectVibrationMultiplePosition |
| `TriggerEffectDualsenseParsers` | Object | ParseStartEndStrengths, ParseStartEndPosition, ParseEffectStrengths |
| `TriggerEffectXboxParsers` | Object | ParseStartEndStrength, ParseStartEndPosition, ParseAmplitude |
| `TwitchActionGroup` | Object |  |
| `TwitchChatMessage` | Object | set_MessageType, get_MessageType |
| `TwitchDropEntry` | Object | Equals, GetHashCode, Equals |
| `TwitchPartyMemberInfo` | Object |  |
| `UMACharacterBodyAnimator` | BodyAnimator | LateUpdate, assignLayerWeights, updateSpineRotation |
| `UVRectTiling` | ValueType | FromXML, ToString, ToXML |
| `UiServerFilter` | IServerListInterface/ServerFilter |  |
| `UniqueIdEqualityComparer` | Object | Equals, GetHashCode |
| `UnityDistantTerrain` | Object | UpdateVoxelChunkInfo, BuildAroundPos, UpdateChunkHeights |
| `UnityDistantTerrainWaterPlane` | Object | createDynamicWaterPlane_Step1, createDynamicWaterPlane_Step2, Cleanup |
| `UnixLinkFile` | Object | Dispose, set_Context, set_Name |
| `UpgradeableReadScope` | ValueType | Dispose |
| `UpscalerMode` | Object | ToString |
| `ValueDisplayFormatters` | Object | RomanNumber, FormatNumberWithMetricPrefix, DateAge |
| `ValuesView` | Object | GetEnumerator, get_Count |
| `ValuesView` | Object | GetEnumerator, get_Count |
| `Vector2F` | ValueType | op_Inequality, get_Length, op_Equality |
| `Vector2d` | ValueType | ToCultureInvariantString, Dot, op_Equality |
| `Vector3Converter` | Vector3> | WriteJson, ReadJson |
| `Vector3d` | ValueType | ToCultureInvariantString, Cross, op_Equality |
| `VideoData` | Object |  |
| `VideoFromXML` | Object | Parse, CreateVideos |
| `VideoManager` | Object | AddVideo, GetVideoData, Init |
| `View` | Object | Cache, Dispose, set_Item |
| `VirtualFileStream` | MemoryStream | Read, ReadByte, get_CanWrite |
| `VisibilityData` | Object |  |
| `VoteDayTimeRange` | Object |  |
| `VoxelMeshExt3dModel` | VoxelMesh | addColliders, Read, CopyToColliders |
| `WaypointSorter` | Object | Compare |
| `WindowsLinkFile` | Object | Dispose, set_Context, set_Name |
| `WrappedStream` | Stream | Dispose, BeginWrite, BeginRead |
| `WriteRequestDetails` | Object | GetNextChunk, HasNextChunk |
| `WriteScope` | ValueType | Dispose |
| `XmlData` | Object | CanAddANewVoice, GetRandomClip, GetClipList |
| `XmlLoadException` | Exception | buildMessage |
| `XmlParserException` | Exception | get_Message, set_Line, get_Line |
| `vp_Activity` | vp_Event | InitFields, TryStart, set_Active |
| `vp_Attempt` | vp_Event | InitFields, Register, Unregister |
| `vp_ComponentPreset` | Object | Parse, Save, Apply |
| `vp_Event` | Object | GetStaticGenericMethod, GetReturnType, RemoveExternalMethodFromField |
| `vp_EventHandler` | MonoBehaviour | CompareMethodSignatures, StoreHandlerEvents, Register |
| `vp_GlobalEventInternal` | Object | ShowUnregisterException, ShowSendException |
| `vp_Message` | vp_Event | InitFields, Register, Unregister |
| `vp_PoolManager` | MonoBehaviour | InstantiateInternal, DestroyInternal, AddObjects |
| `vp_State` | Object | set_Enabled, RemoveBlocker, AddBlocker |
| `vp_StateManager` | Object | CombineStates, SetState, Reset |
| `vp_TargetEventHandler` | Object | Dump, Unregister, Register |
| `vp_Utility` | Object | GetErrorLocation, GetTransformByNameInChildren, GetTransformByNameInAncestors |

## Platform / online SDK (81)

Platform and online-service SDK wrappers: Steam, EOS, Xbox Live, PSN, Discord, GameSparks, entitlements, crossplay, anti-cheat and account/auth plumbing. Client/session features; the dedicated server uses only the auth-adjacent subset.

| Type | base | key methods |
|---|---|---|
| `AchievementData` | Object | DeserializeFromStream, Serialize, SetStatValue |
| `AchievementUtils` | Object | IsCreativeModeActive |
| `AntiCheatClientCS` | Object | EncryptStream, DecryptStream, ConnectToServer |
| `AntiCheatClientManager` | Object | apiInitialized, ConnectToServer, WaitForRemoteAuth |
| `AntiCheatClientP2P` | Object | handlePeerActionRequired, ConnectToServer, Activate |
| `ApplicationStateController` | Object | remove_OnNetworkStateChanged, remove_OnApplicationStateChanged, add_OnNetworkStateChanged |
| `AuthClient` | Object | AuthenticateServer, GetAuthTicket, get_connectInterface |
| `AuthenticationClient` | Object | GetAuthTicket, OnDisconnectFromServer, Init |
| `BaseEventData` | Object | get_SteamBranchName, get_SessionBuild, get_ProviderUserId |
| `CensoredTextResult` | ValueType | get_Success, get_OriginalText, get_CensoredText |
| `DLCTitleStorageManager` | Object | IsDLCPurchasable, GetLocalPlatformNetworkString, FetchFromSource |
| `DownloadableContentValidator` | Object | OpenStore, IsEntitlementPurchasable, IsAvailableOnPlatform |
| `DownloadableContentValidator` | Object | OpenStore, IsEntitlementPurchasable, IsAvailableOnPlatform |
| `EOSSanction` | ValueType | get_ReferenceId |
| `EPlayGroupExtensions` | Object | ToPlayGroup, ToPlayGroup, GetCurrentPlayGroup |
| `ESaveGameProviderStatusExtensions` | Object | IsTerminal |
| `EUserBlockStateExtensions` | Object | IsBlocked |
| `EUserPermsExtensions` | Object | HasMultiplayer, HasHostMultiplayer, HasCrossplay |
| `EnumAchievementDataStatExtensions` | Object | IsSupported |
| `EosUserIdMapper` | Object | QueryMappedExternalAccounts, QueryExternalAccountMappings, QueryMappedExternalAccount |
| `FavoriteServers` | Object | callback, StartSearch, Init |
| `HardwareInfoEventData` | BaseEventData | set_OperatingSystem, set_MemoryRam, set_GpuData |
| `IPlatformApplication` | - | EscapeArg, JoinAndEscapeArgv, GetCurrentRefreshRate |
| `IPlatformUserBlockedDataExtensions` | Object | IsBlocked |
| `IPlatformUserBlockedResults` | - | BlockAll |
| `IRemotePlayerFileStorage` | - | BytesToObject, ObjectToBytes, WriteCachedObject |
| `JoinSessionGameInviteListener` | Object | Init, TakePendingInvite, ConnectToInvite |
| `JoinSessionGameInviteListener` | Object | Init, TakePendingInvite, ConnectToInvite |
| `LANMasterServerAnnouncer` | Object | AdvertiseServer, SendReply, StopServer |
| `LobbyHost` | Object | LobbyCreated_Callback, UpdateGameTimePlayers, StartGameWithLobby |
| `LobbyListAbs` | Object | ParseLobbyData, restartRefreshCo, Disconnect |
| `LobbyListFriends` | LobbyListAbs | queryNextFriend, Lobby_DataUpdate, StartSearch |
| `LobbyListInternet` | LobbyListAbs | RequestLobbies_CallResult, StartSearch, StopSearch |
| `LocalServerDetect` | Object | callback, StartSearch, Init |
| `LoginEventData` | BaseEventData | set_SessionStartTimeStamp, set_Provider, set_Platform |
| `MappedAccountRequest` | Object |  |
| `MasterServerAnnouncer` | Object | StopServer, SetGameServerInfo, Update |
| `MasterServerList` | Object | ServerResponded, StartSearch, StopSearch |
| `MultiplayerInvitationDialogSteam` | Object | ShowInviteDialog, get_CanShow, Init |
| `NetworkClientEos` | Object | Update, ConnectInternal, ConnectionClosedHandler |
| `NetworkClientSteam` | Object | ReceivePackets, ConnectInternal, threadHandlerMethod |
| `NetworkServerEos` | Object | Update, ConnectionRequestHandler, sendBuffers |
| `NetworkServerSteam` | Object | threadHandlerMethod, ReceivePackets, CheckConnections |
| `NetworkUtils` | Object | ParseGameTags2, BuildGameTags, ToAddr |
| `PlatformApplicationStandalone` | Object | get_SupportedResolutions, get_ScreenOptions, SetResolution |
| `PlatformConfiguration` | Object | ParsePlatform, WriteString, ReadFile |
| `PlayerInteraction` | ValueType |  |
| `PlayerInteractionsRecorderMulti` | Object | RecordPlayerInteractions, RecordPlayerInteraction, Init |
| `PlayerReporting` | Object | ReportPlayer, ReportCategories, GetPlayerReportCategoryMapping |
| `RemoteFileStorage` | Object | readCompletedCallback, GetFile, queryFileCallback |
| `RemoteFileStorage` | Object | readCompletedCallback, GetFile, queryFileCallback |
| `RemotePlayerFileStorage` | Object | ReadFileCompleteCallback, ProcessWriteOperation, ProcessReadOperation |
| `RichPresence` | Object | UpdateRichPresence, Init |
| `RichPresence` | Object | UpdateRichPresence, Init |
| `SanctionsCheck` | Object | OnSanctionsQueryResolveAndGatherSanctions, CheckSanctions, CheckSanctionsEnumerator |
| `SanctionsCheckResult` | ValueType | GetAuthFailedMessage, GetReasonMessage, BannedMessage |
| `ServerListAnnouncer` | Object | GetServerPorts, AdvertiseServer, StopServer |
| `ServiceProvider` | Object | Init, Get, Register |
| `SessionsHost` | Object | AdvertiseServer, getPublicIpFromHostedSession, sessionRegisteredCallback |
| `TextCensor` | Object | CensorProfanity, StorageProviderCallback, Update |
| `UdpClientReceiveHandler` | Object | CompleteReceive, BeginReceive, CompleteReceiveAsync |
| `UdpClientSendHandler` | Object | BeginSend, CompleteSend, CompleteSendAsync |
| `UserBase` | Object | connectLogin, removeNotifications, addNotifications |
| `UserDataRoaming` | UserDataRoamingAbs | get_OptionalSaveRoaming, get_NoSaveRoaming, get_ForcedSaveRoaming |
| `UserDataRoamingAbs` | Object | ValidateStoragePref, get_SaveRoamingEnabled, ValidateRoamingMode |
| `UserDataRoamingGameCore` | UserDataRoamingAbs | get_SaveRoamingMode, get_DefaultSaveStorage |
| `UserDataRoamingMultiPlatform` | UserDataRoamingAbs | get_SaveRoamingMode, get_DefaultSaveStorage |
| `UserDataRoamingPS5` | UserDataRoamingAbs | get_SaveRoamingMode, get_DefaultSaveStorage |
| `UserDetailsRequest` | Object |  |
| `UserDetailsServiceEos` | Object | RequestUserDetailsUpdate, Init |
| `UserIdentifierFactory` | AbsUserIdentifierFactory | FromId |
| `UserIdentifierFactory` | AbsUserIdentifierFactory | FromId |
| `UserIdentifierFactory` | AbsUserIdentifierFactory | FromId |
| `UserIdentifierFactory` | AbsUserIdentifierFactory | FromId |
| `UserIdentifierFactory` | AbsUserIdentifierFactory | FromId |
| `UserIdentifierLocal` | PlatformUserIdentifierAbs | Equals, get_ReadablePlatformUserIdentifier, get_PlatformIdentifierString |
| `UserIdentifierPSN` | PlatformUserIdentifierAbs | Equals, GetHashCode, set_AccountId |
| `UserIdentifierXbl` | PlatformUserIdentifierAbs | Equals, get_Xuid, get_ReadablePlatformUserIdentifier |
| `UserServer` | UserBase | fetchDeviceId, Login, eosLoggedIn |
| `VirtualKeyboard` | Object | Open, GamePadTextInputDismissed_Callback, Init |
| `XblPlatformApi` | Object | add_ClientApiInitialized, remove_ClientApiInitialized, InitClientApis |

## Client audio / dynamic music (56)

The audio manager and the dynamic-music system (themes, layers, threat levels, content loaders). Client-presentation only.

| Type | base | key methods |
|---|---|---|
| `AbstractConfiguration` | Object | ParseFromXml, GetBufferSize, Get |
| `AbstractDayTimeTracker` | AbstractFilter |  |
| `AbstractFilter` | Object |  |
| `AbstractMusicTimeTracker` | AbstractFilter |  |
| `Adventure` | FixedLayerMixer> | PlayCoroutine |
| `AmbientAudioController` | Object | SetAmbientVolume, OnGamePrefChanged, get_Instance |
| `AudioBiome` | Object | TransitionFrom, TransitionTo, UnPause |
| `AudioDeviceConfig` | Object | getCurrentDeviceCallbackFn, ApplyDevicesFound, getDevices |
| `AudioGamepadRumbleSource` | Object | GetSample, SetAudioSource, Clear |
| `AudioGroup` | GameOptionsReset/EnumGamePrefGroup | Reset, get_VersionId |
| `BloodmoonClipSet` | LayeredContent | ParseFromXml, GetSample |
| `BloodmoonConfiguration` | AbstractConfiguration | ParseFromXml, getState, CountFor |
| `BloodmoonLayerMixer` | BloodmoonConfiguration> | get_Item, Load |
| `ClipAdapter` | Object | SetPaths, LoadImmediate, GetSample |
| `ClipPairAdapter` | Object | GetSample, SetPaths, Unload |
| `ClipSet` | LayeredContent | ParseFromXml, GetSample |
| `ClipUtils` | Object | LoadClipFrom, StripClip, LoadClipImmediate |
| `Combat` | CombatLayerMixer> | PlayCoroutine |
| `CombatLayerMixer` | FixedLayerMixer | updateHyperbar, Load |
| `Conductor` | Object | Update, Init, CleanUp |
| `Content` | Object | ParseFromXml, CreateWrapper, set_Section |
| `ContentLoader` | Object | Cleanup, Start, get_Instance |
| `ContentPlayer` | Object | Stop, Play, UnPause |
| `ContentQueue` | Object | Next, Clear, get_IsReady |
| `Curve` | Object |  |
| `DynamicMusicSystemPassArbiter` | ValueType | SetBoolContainer, OnGamePrefChanged, set_IsGameUnPaused |
| `ExponentialCurve` | LinearCurve | GetMixerValue |
| `FixedConfiguration` | AbstractConfiguration | ParseLayers, ParseFromXml, CountFor |
| `FixedConfigurationLayerData` | Object | Add, get_Count |
| `FixedLayerMixer` | FixedConfiguration> | get_Item, get_IsFinished, updateHyperbar |
| `FrequencyLimiter` | AbstractFilter | UpdateParameters, Filter, OnGamePrefChanged |
| `InstrumentID` | String> | Unload, remove_OnLoadFinished, add_OnLoadFinished |
| `LayerState` | Object | get_Count |
| `LayerStreamer` | Object | FillStream, OnClipSetLoad, Tick |
| `LayeredContent` | Content | ReadyQueuesImmediate, SetData, Get |
| `LinearCurve` | Curve | GetLine, GetMixerValue |
| `LogarithmicCurve` | LinearCurve | GetMixerValue |
| `MixerController` | Object | Init, SetAllCombatVolume, SetDynamicMusicVolume |
| `MusicGroup` | ThreatLevel> | Cleanup, InitStatic |
| `MusicTimeTracker` | AbstractMusicTimeTracker | ToString, Filter, OnStop |
| `Section` | ContentPlayer | Play, CleanUp, FadeIn |
| `SectionSelector` | Object | Select, Notify |
| `SingleClip` | Content | ParseFromXml, Unload, Load |
| `SingleClipPlayer` | Section | Init, GetSingleClip, InitializationCoroutine |
| `Song` | SingleClipPlayer | PlayCoroutine |
| `SoundRange` | Object |  |
| `StreamerMaster` | Object | ReplaceCurrentStreamer, Tick, get_IsReplacementNecessary |
| `SubtitleSpeakerColor` | Object |  |
| `Theme` | SingleClipPlayer | PlayCoroutine, InitializationCoroutine |
| `ThreatLevel` | Layer> |  |
| `ThreatLevelStreamer` | Object | Play, get_IsPlaying, get_InitFinished |
| `TransitionManager` | Object | Tick, Init, SetDynamicMusicVolume |
| `VoiceAudioDevice` | Object |  |
| `VoiceAudioDeviceDefault` | IPartyVoice/VoiceAudioDevice | ToString, get_Identifier |
| `VoiceAudioDeviceNotFound` | IPartyVoice/VoiceAudioDevice | ToString, get_Identifier |
| `VoiceHelpers` | Object | GetPlayerDiscordVoiceState, GetPlayerVoiceState, pushToTalkButtonValid |

## Twitch client / PubSub (53)

The Twitch integration client: API DTOs, PubSub message types, and base command/event classes. The server hosts twitch actions; the API polling is client-side.

| Type | base | key methods |
|---|---|---|
| `BasePubSubMessage` | Object | set_type, set_nonce, get_type |
| `BaseTwitchCommand` | Object | SetupCommandTextList, CheckAllowed, GetPermission |
| `ConfigContent` | Object |  |
| `Entitlement` | Object |  |
| `ExtensionDeleteBitActionsRequestData` | Object |  |
| `FulfillmentPayload` | Object |  |
| `GiftSubEntry` | Object | Update, AddSub |
| `PubSubBitRedemptionMessage` | BasePubSubMessage | Deserialize |
| `PubSubChannelPointMessage` | BasePubSubMessage | Deserialize |
| `PubSubGoalMessage` | BasePubSubMessage | set_type, set_data, get_type |
| `PubSubListenMessage` | BasePubSubMessage |  |
| `PubSubStatusMessage` | Object |  |
| `PubSubStatusRequestData` | Object |  |
| `PubSubSubscriptionRedemptionMessage` | BasePubSubMessage | set_user_name, set_user_id, set_sub_plan_name |
| `SetConfigRequestData` | Object |  |
| `SetDevConfigRequestData` | Object |  |
| `TwitchChannelPointEventEntry` | BaseTwitchEventEntry | SetupRewardEntry, DeleteCustomRewardsDelete, CreateCustomRewardPost |
| `TwitchCommandCheckCredit` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandCheckPoints` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandCommands` | BaseTwitchCommand | Execute, get_LocalizedCommandNames, get_CommandText |
| `TwitchCommandDebug` | BaseTwitchCommand | ExecuteConsole, get_LocalizedCommandNames, get_CommandText |
| `TwitchCommandDisableCommand` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandEnableCommand` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandGamestage` | BaseTwitchCommand | get_LocalizedCommandNames, get_CommandText, ExecuteConsole |
| `TwitchCommandPauseCommand` | BaseTwitchCommand | Execute, get_LocalizedCommandNames, ExecuteConsole |
| `TwitchCommandRedeemBits` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandRedeemCharity` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandRedeemCreatorGoal` | BaseTwitchCommand | Execute, get_LocalizedCommandNames, ExecuteConsole |
| `TwitchCommandRedeemGiftSub` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandRedeemHypeTrain` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandRedeemRaid` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandRedeemSub` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandRemoveViewer` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandResetCooldowns` | BaseTwitchCommand | ExecuteConsole, Execute, get_LocalizedCommandNames |
| `TwitchCommandSetBitPot` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandSetCooldown` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandSetPot` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandTeleportBackpack` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCommandUnpauseCommand` | BaseTwitchCommand | Execute, get_LocalizedCommandNames, ExecuteConsole |
| `TwitchCommandUseProgression` | BaseTwitchCommand | Execute, ExecuteConsole, get_LocalizedCommandNames |
| `TwitchCreatorGoalEventEntry` | BaseTwitchEventEntry | IsValid |
| `TwitchEntitlementManager` | Object | OnDropsUpdated, Init, HasEntitlement |
| `TwitchEventEntry` | BaseTwitchEventEntry | IsValid |
| `TwitchEventPreset` | Object | RemoveChannelPointRedemptions, AddChannelPointRedemptions, get_HasCustomEvents |
| `TwitchHypeTrainEventEntry` | TwitchEventEntry |  |
| `TwitchLeaderboardEntry` | Object |  |
| `TwitchMessageEntry` | Object |  |
| `TwitchSpawnedBlocksEntry` | Object | CheckPos, RemoveBlocks, RemoveBlock |
| `TwitchSubEventEntry` | TwitchEventEntry | IsValid, GetSubTier, Description |
| `TwitchTopic` | Object | Subscription, HypeTrain, CreatorGoal |
| `TwitchVoteGroup` | Object | ShuffleVoteTypes, GetNextVoteType |
| `TwitchVoteType` | Object | ParseProperties, CanUse, IsInPreset |
| `UpdateMessage` | Object | GetLocalizedPPRateValue, ModdedValueLocalized, DifficultyValueLocalized |

## Client render / avatar / presentation (22)

Rendering, avatar controllers, camera, particles, post-processing and presentation helpers. Client-only.

| Type | base | key methods |
|---|---|---|
| `AnimationDelays` | ValueType |  |
| `AnimationGunjointOffsets` | ValueType |  |
| `AnimationStates` | Object |  |
| `AtmosphereEffect` | Object | Load |
| `AvatarCharacterController` | AvatarMultiBodyController | GetThirdPersonDeathStates, GetThirdPersonReloadStates, GetFirstPersonReloadStates |
| `CameraPerspectives` | Object | Load, Save, GetFullFilePath |
| `CharacterControllerKinematic` | CharacterControllerAbstract | Update, SetHeight, Move |
| `CharacterControllerUnity` | CharacterControllerAbstract | SetSize, set_enableOverlapRecovery, SetStepOffset |
| `GraphicsGroup` | GameOptionsReset/EnumGamePrefGroup | Reset, get_VersionId, NeedsReset |
| `MeshDataUtils` | Object | SetAttributes, CalculateNormals, AddTriangleNormal |
| `MeshDescriptionCollection` | MonoBehaviour | Init, SetTextureArraysFilter, LoadTextureArraysForQuality |
| `MeshLists` | Object | Reset, ReturnList, GetList |
| `MeshMorph` | ScriptableObject | GetMorphedSkinnedMesh, Init, IsInstance |
| `MeshPrefabSet` | Object |  |
| `MeshStats` | Object | ToProperties, FromProperties |
| `TextureAtlas` | Object | LoadTextureAtlas, Cleanup |
| `TextureAtlasBlocks` | TextureAtlas | Cleanup, LoadTextureAtlasFromMetadata, LoadTextureAtlas |
| `TextureAtlasExternalModels` | TextureAtlas | LoadTextureAtlas |
| `TextureAtlasTerrain` | TextureAtlasBlocks | LoadTextureAtlas, Cleanup |
| `TextureScale` | Object | ThreadedScale, BilinearScale, PointScale |
| `VertexEntry` | ValueType |  |
| `VertexKey` | ValueType | GetHashCode, Equals |

## Editor / dev tools / metrics (9)

Editor helpers, debug/benchmark tooling and metrics collectors. Developer and client diagnostics.

| Type | base | key methods |
|---|---|---|
| `AutomationScript` | Object | Validate, ResolveSessionDir, Describe |
| `CallbackMetric` | Object | AppendLastValue, set_Header, get_Header |
| `ConstantValueMetric` | Object | AppendLastValue, set_Header, get_Header |
| `DebugWrapper` | Object | DebugReadWriteScope, DebugReadScope, DebugEnumerator |
| `DebugWrapperException` | Exception |  |
| `ProfilerPlatformCorrections` | Object | TotalTracked, Graphics, Native |
| `ProfilerRecorderMetric` | Object | AppendLastValue, set_Header, Cleanup |
| `ProfilerScope` | ValueType | Dispose |
| `SelectionCategory` | Object | AddBox, Clear, SetVisible |

## Arity generics appendix (62)

Generic types with arity (`` `1``/`` `2`` suffixes) from the classified set; the
census credits them by their arity-stripped base name.

| Type | base | key methods |
|---|---|---|
| `AddressableAssetHandle`1` | Object | ToString, Release, Copy |
| `AddressableAssetsRequestTask`1` | LoadManager/AssetsRequestTask`1<T> | StartAssetsRequest, CollectResults, get_INTERNAL_IsPending |
| `AddressableRequestTask`1` | LoadManager/AddressableRequestTask`1<T> | get_IsDone, get_INTERNAL_IsPending, Load |
| `Array3DWithOffset`1` | Object | Contains, GetIndex, set_Item |
| `ArrayDynamicFast`1` | Object | Contains, Add, Clear |
| `ArrayListMP`1` | Object | AddRange, Alloc, Add |
| `AssetBundleRequestTask`1` | LoadManager/AssetRequestTask`1<T> | LoadSync, CompleteNow, Complete |
| `AssetRequestTask`1` | LoadManager/LoadTask | get_keepWaiting, get_IsDone, get_Asset |
| `AssetsRequestTask`1` | LoadManager/AssetsRequestTask`1<T> | StartAssetsRequest, CollectResults, get_INTERNAL_IsPending |
| `BackedArraySingleView`1` | Object | Dispose, Flush, CreateView |
| `CachedStringFormatter`1` | Object | Format, Format |
| `CachedStringFormatter`2` | Object | Format, Format |
| `CachedStringFormatter`3` | Object | Format, Format |
| `CachedStringFormatter`4` | Object | Format, Format |
| `Cells`1` | Object | CompareTest, Stats, ToArray |
| `DataItem`1` | Object | ToString, remove_OnChangeDelegates, add_OnChangeDelegates |
| `DatabaseWithFixedDS`2` | Object | read, write, Save |
| `DictionaryChangedEventArgs`2` | EventArgs | get_Value, get_Key, get_Action |
| `DictionaryKeyList`2` | Object | Replace, Remove, Add |
| `DictionaryKeyValueList`2` | Object | Remove, Add, Set |
| `DictionaryLinkedList`2` | Object | Remove, Add, Set |
| `DictionaryNameId`1` | Object | Get, Contains, Add |
| `DictionarySave`2` | Object | Deserialize, Serialize, RemoveAllMarked |
| `DynamicObjectPool`1` | Object | Allocate, push, Free |
| `EmptyAddressableRequestTask`1` | LoadManager/AddressableRequestTask`1<T> | get_IsDone, get_INTERNAL_IsPending, Load |
| `EnumDictionary`2` | Dictionary`2<TKey,TValue> |  |
| `EnumInfoCache`1` | Object | TryParse, Parse, GetName |
| `FastEnumIntEqualityComparer`1` | Object | Equals, GetHashCode, ToInt |
| `ITileArea`1` | - | Cleanup |
| `IntermediateDataWrapper`1` | Object | UpdateBuffer, NextPow2, ApplyToMaterial |
| `LayerMixer`1` | Object | Unload, Load, set_Sect |
| `LayeredSection`1` | Section | FillStream, Reset, Init |
| `LinkedDictionary`2` | Object | set_Item, Add, TryGetValue |
| `LoosePool`1` | Object | Free, GetSize, Alloc |
| `ManyToManyDictionary`2` | Object | Remove, RemoveByValue, RemoveByKey |
| `MemoryBackedArray`1` | Object | GetMemoryUnsafeInternal, GetStaticHandle, GetReadOnlySpan |
| `MemoryPooledArray`1` | Object | Free, Alloc, FreeAll |
| `MemoryPooledObject`1` | Object | Free, Cleanup, FreeSync |
| `ModEventInterruptible`1` | ModEvents/ModEventAbs`1<ModEvents/ModEventInterruptibleHandlerDelegate`1<TData>> | Invoke |
| `NativeSafeHandle`1` | ValueType | Dispose, get_Target |
| `ObservableDictionary`2` | Object | set_Item, Clear, remove_EntryUpdatedValue |
| `OneToManyDictionary`2` | Object | TryGetByKey, RemoveByValue, RemoveByKey |
| `OptimizedList`1` | Object | AddSafe, AddRange, AddRange |
| `PinnedBufferRef`1` | ValueType | AsBytes, CreateNativeArray, AsSpan |
| `ReadOnlyDictionaryWrapper`3` | Object | TryGetValue, get_Item, get_Values |
| `ResourceRequestTask`1` | LoadManager/AssetRequestTask`1<T> | Complete, get_INTERNAL_IsPending, CompleteNow |
| `StateHistory`1` | Object | Add, ToString, Clear |
| `StringSpanDictionary`1` | Object | TryGetStringFromHashedKeys, AddHash, RemoveHash |
| `TList`1` | Object | AddIfNotExist, BinarySearch, LastIndexOf |
| `TQueue`1` | Object | EnqueueAll, EnqueueAll, DequeueAll |
| `UnsafeChunkData`1` | ValueType | Set, CheckSameValue, CalculateOwnedBytes |
| `UnsafeChunkXZMap`1` | ValueType | CalculateOwnedBytes, Clear, Set |
| `UnsafeFixedBuffer`1` | ValueType | AddThreadSafe, Dispose, CalculateOwnedBytes |
| `XUiC_ComboBoxEnum`1` | XUiC_ComboBox`1<TEnum> | attributeValues, changeIndex, set_Value |
| `XUiC_ComboBoxList`1` | XUiC_ComboBox`1<TElement> | attributeValues, set_SelectedIndex, ChangeIndex |
| `XUiC_ComboBoxOrdinal`1` | XUiC_ComboBox`1<TValue> | set_Value, OnOpen, UpdateLabel |
| `XUiC_ComboBox`1` | XUiC_ComboBoxBase | TryPageUp, TryPageDown, setRelativeValue |
| `XUiC_DMBaseList`1` | XUiC_List`1<T> | Init, pageContentsChangedHandler, childElementHovered |
| `XUiC_List`1` | XUiController | Update, updateCurrentPageContents, set_SelectedEntry |
| `XUiListEntry`1` | Object | set_UiDirty, get_UiDirty, MatchesSearch |
| `vp_GlobalEventReturn`4` | Object | Send, Register, Unregister |
| `vp_Value`1` | vp_Event | InitFields, Unregister, Register |
## Related

- [out-of-scope-surface.md](out-of-scope-surface.md) - the authoritative client/3rd-party classification.
- [coverage.md](coverage.md) - the census and how these tiers are counted.
