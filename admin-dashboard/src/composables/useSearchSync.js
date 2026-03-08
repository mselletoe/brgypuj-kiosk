import { onMounted, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";

export function useSearchSync(searchRef) {
  const route = useRoute();
  const router = useRouter();

  onMounted(async () => {
    await nextTick();
    const q = route.query.q;
    if (q) {
      searchRef.value = decodeURIComponent(q);
      router.replace({ query: {} });
    }
  });
}
