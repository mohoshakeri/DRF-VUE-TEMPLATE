import type {MessageStatus} from "/src/constants/ENUMS";
import {MESSAGE_STATUS_PRIMARY} from "/src/constants/ENUMS";
import {useGlobalStore} from "/src/stores/global";

export async function sendMessage(
  content: string,
  status: MessageStatus = MESSAGE_STATUS_PRIMARY,
): Promise<void> {
  const store = useGlobalStore();
  store.showMessage(content, status);
}
